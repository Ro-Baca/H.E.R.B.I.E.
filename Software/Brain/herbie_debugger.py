# herbie_combined_app.py
import serial
import time
import json
import threading
from flask import Flask, render_template, request, redirect, url_for
import sys

# --- Configuración ---
AVR_WIN = 5       
SERIAL_PORT = '/dev/ttyS0'
BAUD_RATE = 9600

MIN_MOISTURE = 10.0   # % Humedad Suelo: Por debajo -> DRY
MAX_TEMP = 50.0       # °C Temperatura: Por encima -> HOT
MIN_TEMP = 15.0       # °C Temperatura: Por debajo -> COLD
MIN_LIGHT = 10.0     # Lux Luz: Por debajo -> SAD
MAX_LIGHT = 1000.0   # Lux Luz: Por encima -> TIRED

thresholds = {
    "MIN_MOISTURE": MIN_MOISTURE,
    "MAX_TEMP": MAX_TEMP,
    "MIN_TEMP": MIN_TEMP, 
    "MIN_LIGHT": MIN_LIGHT, 
    "MAX_LIGHT": MAX_LIGHT 
}

# --- Variables Globales ---
ser = None 
readings_buffer = [] 
latest_average_data = { # Inicializado con claves
    'timestamp': None, 'moisture': None, 'temperature': None, 
    'humidity': None, 'light': None
}
data_lock = threading.Lock()
new_average_calculated = False 
flag_lock = threading.Lock()
current_state_on_pico = None # Para recordar el último estado enviado
state_lock = threading.Lock() # Lock para esta nueva variable

# --- Lógica de Promediado ---
def calculate_and_update_average(buffer):
    """
    Calcula el promedio, determina el estado, envía el comando (si cambia) y 
    actualiza la variable global de datos.
    """
    
    global latest_average_data, data_lock

    # --- Cálculo de promedios ---
    valid_moisture = [r['moisture'] for r in buffer if r.get('moisture') is not None]
    valid_temp = [r['temperature'] for r in buffer if r.get('temperature') is not None]
    valid_humidity = [r['humidity'] for r in buffer if r.get('humidity') is not None]
    valid_light = [r['light'] for r in buffer if r.get('light') is not None]

    avg_moisture = round(sum(valid_moisture) / len(valid_moisture), 2) if valid_moisture else None
    avg_temp = round(sum(valid_temp) / len(valid_temp), 2) if valid_temp else None
    avg_humidity = round(sum(valid_humidity) / len(valid_humidity), 2) if valid_humidity else None
    avg_light = round(sum(valid_light) / len(valid_light), 2) if valid_light else None

    average_data_readings = {
        "moisture": avg_moisture, "temperature": avg_temp,
        "humidity": avg_humidity, "light": avg_light,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S") 
    }

    print(f"DEBUG: avg_light = {avg_light}")

    # --- Lógica de Estado Automático ---
    current_state = determine_plant_state(avg_moisture, avg_temp, avg_light, thresholds)

    # --- Añade el estado al diccionario de datos ---
    average_data_to_display = average_data_readings.copy() # Copia los datos
    average_data_to_display["state"] = current_state

    with data_lock:
        latest_average_data = average_data_to_display # Guarda el diccionario con el estado

    with flag_lock:
        new_average_calculated = True

    print(f"--- Datos prtomediados ---")
    print(f"Estado: {current_state}")


# --- determinar estadod e la planta ---
def determine_plant_state(avg_moisture, avg_temp, avg_light, thresholds):
    """
    Determina el estado de la planta basado en las lecturas promedio y los umbrales.
    Sigue un orden de prioridad: Humedad > Temperatura > Luz.
    """
    
    # Prioridad 1: Humedad
    if avg_moisture is None or avg_moisture == 0:
        return "DEAD" # Sensor desconectado o completamente seco = muerto
    if avg_moisture < thresholds["MIN_MOISTURE"]:
        return "DRY"
        
    # Prioridad 2: Temperatura (solo si la humedad está bien)
    if avg_temp is not None: # Solo checar si tenemos lectura válida
        if avg_temp > thresholds["MAX_TEMP"]:
            return "HOT"
        if avg_temp < thresholds["MIN_TEMP"]:
            return "COLD"
            
    # Prioridad 3: Luz (solo si humedad y temperatura están bien)
    if avg_light is not None: # Solo checar si tenemos lectura válida
        if avg_light < thresholds["MIN_LIGHT"]:
            return "SAD" 
        if avg_light > thresholds["MAX_LIGHT"]:
            return "TIRED"
            
    # Si ninguna condición de "problema" se cumplió, todo está OK
    return "OK"


def send_state_command(state_name):
    """
    Envía un comando de estado a la Pico, SOLO si es diferente al último enviado.
    Actualiza el estado recordado.
    """
    global ser, current_state_on_pico, state_lock
    
    state_name = state_name.upper() # Asegura mayúsculas
    
    with state_lock: # Acceso seguro a la variable compartida
        # Comprueba si el estado es NUEVO
        if state_name != current_state_on_pico:
            command_json = f'{{"command": "set_state", "type": "{state_name}"}}\n'
            try:
                if ser:
                    print(" ")
                    print(f"H.E.R.B.I.E. state: {state_name}")
                    ser.write(command_json.encode('utf-8'))
                    current_state_on_pico = state_name # Actualiza el estado recordado SÓLO si se envió
                else:
                     print("⚠️ No se pudo enviar comando: Puerto serie no disponible.")
            except Exception as e:
                print(f"Error al escribir en el puerto serie: {e}")
        # else: # Opcional: imprimir si el estado no cambió
            # print(f"ℹ️ Estado ya es {state_name}, no se envía comando.")

# --- Hilo de Escucha Serial (Modificado) ---
def serial_listener_loop():
    global ser, readings_buffer
    print("Hilo Lector: Iniciando...")
    # No ponemos el delay aquí, lo controla el main

    while True:
        line_processed = False # Bandera para saber si hicimos algo
        try:
            # Intenta leer solo si hay datos, sin bloquear mucho tiempo
            if ser and ser.in_waiting > 0:
                line_bytes = ser.readline()
                if line_bytes:
                    line_processed = True # Marcamos que leímos algo
                    json_string = line_bytes.decode('utf-8', errors='ignore').strip()
                    if json_string and json_string.startswith('{') and json_string.endswith('}'):
                        try:
                            data = json.loads(json_string)
                            readings_buffer.append(data)
                            buffer_count = len(readings_buffer)
                            print(f"Lectura Recibida ({buffer_count}/{AVR_WIN})") 

                            if buffer_count >= AVR_WIN:
                                calculate_and_update_average(readings_buffer)
                                readings_buffer.clear()
                                
                        except json.JSONDecodeError:
                            print(f"‼️ Hilo Lector: Error JSON: {json_string}")
                    elif json_string:
                         print(f"‼️ Hilo Lector: Recibido no-JSON: {json_string}")

        except serial.SerialException as e:
            print(f"Hilo Lector: Error Serial Grave: {e}")
            time.sleep(5) 
        except Exception as e:
            print(f"Hilo Lector: Error Inesperado: {e}")
            time.sleep(1)

        # Si no procesamos nada, dormimos un poco más para ceder CPU
        if not line_processed:
            time.sleep(0.1) 
        else:
             time.sleep(0.01) # Si leímos, dormimos muy poco

# --- Aplicación Web Flask (Sin cambios) ---
app = Flask(__name__)

def get_latest_average_from_memory():
    global latest_average_data, data_lock
    with data_lock:
        return latest_average_data.copy()

@app.route('/')
def index():
    """Muestra el dashboard. Solo imprime si hay datos nuevos"""
    global new_average_calculated, flag_lock, thresholds
    current_average_data = get_latest_average_from_memory()
    should_print_message = False # Variable local para decidir si imprimir
    with flag_lock:
        if new_average_calculated:
            should_print_message = True
            new_average_calculated = False

    # Imprime el mensaje SOLO si la bandera estaba activa
    if should_print_message:
        print(f"Datos: {current_average_data}")

    return render_template('debugger.html', data=current_average_data, thresholds=thresholds)

@app.route('/send_command', methods=['POST'])
def handle_command():
    """Ruta para recibir el comando manual del dropdown."""
    if request.method == 'POST':
        selected_emotion = request.form.get('emotion') # Usar .get() es más seguro
        if selected_emotion: # Asegura que no esté vacío
            send_state_command(selected_emotion) # Llama a la función centralizada
    return redirect(url_for('index')) # Redirige de vuelta a la página principal



# --- Inicio del Programa ---
if __name__ == '__main__':
    # 1. Intenta abrir el puerto serie
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.1) # Timeout más corto
        ser.flush()
        print("Puerto serie conectado.")
    except serial.SerialException as e:
        print(f"Error fatal abriendo puerto serie {SERIAL_PORT}: {e}")
        exit()

    # 2. Inicia el hilo de escucha serial (que calcula promedios y envía estados automáticos)
    listener_thread = threading.Thread(target=serial_listener_loop, daemon=True)
    listener_thread.start()

    # 3. Envía el comando STARTUP a la Pico
    send_state_command("STARTUP")

    # 3. Inicia el servidor web Flask (que recibe comandos manuales de la GUI)
    print(f"Iniciando servidor web en http://0.0.0.0:5000")
    try:
        # debug=False es más seguro, threaded=True puede ayudar con hilos
        app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
    except KeyboardInterrupt:
        print("\nCerrando servidor web...")
    finally:
        send_state_command("SHUTDOWN")
        time.sleep(1)
        
        if ser and ser.is_open:
            ser.close()
            print("Puerto serie cerrado.")