# simple_serial_reader_styled.py
# Lee datos JSON del puerto serie y los imprime, estilo listener.py

import serial
import time
import json

# --- Configuración del puerto serie ---
try:
    # '/dev/ttyS0' es el puerto serial en los pines GPIO de la Pi Zero
    # La velocidad (9600) debe coincidir con la de la Pico
    ser = serial.Serial('/dev/ttyS0', 9600, timeout=1)
    ser.flush() # Limpia el buffer
    print("✅ Puerto serie conectado. Escuchando datos...")
except serial.SerialException as e:
    print(f"🚨 Error en Puerto Serie: {e}")
    exit() # Sale si no puede conectar

def main():
    """
    Bucle principal para escuchar datos e imprimirlos.
    """
    while True:
        try:
            # Verifica si hay datos esperando
            if ser.in_waiting > 0:
                line_bytes = ser.readline()
                
                # Si se leyó algo (no fue solo un timeout)
                if line_bytes:
                    # Decodifica de bytes a string y quita espacios extra
                    json_string = line_bytes.decode('utf-8', errors='ignore').strip()
                    
                    # Intenta decodificar el JSON solo si la línea no está vacía
                    if json_string:
                        try:
                            data = json.loads(json_string)
                            # Imprime los datos recibidos con el formato deseado
                            print(f"  -> Lectura recibida: {data}")
                        except json.JSONDecodeError:
                            # Imprime error si el JSON es inválido
                            print(f"‼️ Error en JSON: {json_string}")
                            
        except KeyboardInterrupt:
            # Permite detener el script con Ctrl+C
            print("\nDetenido por el usuario.")
            break
        except serial.SerialException as e:
            print(f"\n🚨 Error de Puerto Serie: {e}")
            break # Sale si hay un error grave de conexión
        except Exception as e:
            print(f"\nError inesperado: {e}")
            time.sleep(2) # Pausa antes de reintentar

# --- Bucle Principal ---
if __name__ == "__main__":
    try:
        main()
    finally:
        # Asegura que el puerto serie se cierre al salir
        if ser and ser.is_open:
            ser.close()
            print("Puerto serie cerrado.")