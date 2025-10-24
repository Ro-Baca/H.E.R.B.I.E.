from machine import Pin, ADC, UART
import time
from dht import DHT11, InvalidPulseCount
import ujson

# --- Constantes ---
temp_pin = 16
moist_pin = 26
pwr_led_pin = 15
init_delay = 2       # Tiempo de calentamiento de los sensores
sleep_interval = 1   # Intervalo entre lecturas (puedes ajustarlo)

# --- Configuración del UART (Comunicación Serial) ---
uart = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1))
print("UART configurado. Usando formato JSON...")

# --- Configuración de Sensores y Actuadores ---
pwr_led = Pin(pwr_led_pin, Pin.OUT)
mois_sens = ADC(moist_pin)
temp_sensor = DHT11(Pin(temp_pin, Pin.IN))

# --- Valores de Calibración del Sensor de Humedad ---
val_dry = 65535      # Valor obtenido con el sensor totalmente seco
val_mois = 19028     # Valor obtenido con el sensor sumergido en agua

# --- Funciones ---
def get_moist():
    """
    Lee el sensor de humedad YL-69, calcula un porcentaje y devuelve el valor.
    """
    moisture_read = mois_sens.read_u16()
    val_range = val_dry - val_mois
    if val_range <= 0: return 0.0
    sens_read = moisture_read - val_mois
    moist_sensor_data = 100 - (sens_read * 100 / val_range)
    return max(0.0, min(100.0, moist_sensor_data)) # Mantiene el % entre 0 y 100

def get_temp():
    """
    Lee el sensor de temperatura y humedad DHT11, manejando posibles fallos.
    """
    try:
        temp_sensor.measure()
        return (temp_sensor.temperature, temp_sensor.humidity)
    except (OSError, InvalidPulseCount):
        return (None, None) # Devuelve None si hay un error

def send_data(moist_sensor_data, temp_sensor_data, humid_sensor_data):
    """
    Crea un diccionario, lo convierte a JSON y lo envía por UART.
    """
    # Crea el diccionario de Python
    data_dict = {
        "moisture": round(moist_sensor_data, 1),
        "temperature": temp_sensor_data,
        "humidity": humid_sensor_data
    }

    # Convierte el diccionario a una cadena de texto JSON
    json_string = ujson.dumps(data_dict)

    # Envía la cadena JSON seguida de un carácter de nueva línea
    print(f"Enviando: {json_string}")
    uart.write(json_string + '\n')

def main():
    """
    Bucle principal del programa.
    """
    print("Iniciando sistema...")
    pwr_led.value(1) # Enciende el LED para indicar que el programa está corriendo
    time.sleep(init_delay)
    
    try:
        while True:
            # Mide los sensores
            moist_data = get_moist()
            temp_data, humid_data = get_temp()
            
            # Envía los datos
            send_data(moist_data, temp_data, humid_data)
            
            # Espera para la siguiente lectura
            time.sleep(sleep_interval)
            
    except KeyboardInterrupt:
        # Esto se activa si detienes el script manualmente (ej. con Ctrl+C)
        print("Programa detenido por el usuario.")
    finally:
        # Este bloque se ejecuta siempre al salir del try, ya sea por error o interrupción
        print("Apagando sistema...")
        pwr_led.value(0) # Apaga el LED para indicar que el programa se detuvo

# --- Punto de entrada del programa ---
if __name__ == "__main__":
    main()