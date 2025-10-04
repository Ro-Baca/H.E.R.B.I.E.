
import serial
import time
import json

# --- Tresholds ---
min_moist = 30.0
max_temp = 30.0
min_temp = 15.0

# --- Serial port config ---
try:
    # '/dev/ttyS0' is the default serial port in the GPIO
    # The speed must match the pico speed (9600)
    
    ser = serial.Serial('/dev/ttyS0', 9600, timeout=1)
    ser.flush() # cleans buffer
    print("Serial port connected. waiting for data...")
except serial.SerialException as e:
    print(f"Error in the serial port: {e}")
    print("Make sure to disable the consol serial in the raspi-config")
    exit()

def get_data(data):
    """
    Reads received data
    """
    print("\n--- Data received ---")
    
    # Accedemos a los datos por su clave (en minúsculas, como lo envía la Pico)
    moist_sensor_data = data["moisture"]
    temp_sensor_data = data["temperature"]

    print(f"Moisture: ({moist_sensor_data:.1f}%)")
    if temp_sensor_data is not None:
        print(f"Temperature: ({temp_sensor_data:.1f}°C)")
    else:
        print("Temperature: Invalid reading")

def main():
    while True:
        try:
            # Check for data in the buffer 
            if ser.in_waiting > 0:
                # Reads one line until '\n'
                linea_bytes = ser.readline()
                
                # Decode the message into a string
                json_string = linea_bytes.decode('utf-8').rstrip()
                
                # Convert JSON to a python dictionary
                datos = json.loads(json_string)
                
                # Calls read function Llama a la función que toma las decisiones
                get_data(datos)
                
        except json.JSONDecodeError:
            print(f" Error: Unable to read JSON. Message: {json_string}")
        except KeyboardInterrupt:
            print("\n System stop")
            break
        except Exception as e:
            print(f"Unexpected error: {e}")
            time.sleep(2) # Pausa for retry

# --- Start main ---
if __name__ == "__main__":
    main()