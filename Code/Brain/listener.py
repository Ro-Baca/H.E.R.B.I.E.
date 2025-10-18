import serial
import time
import json
import sqlite3
from datetime import datetime

# --- Configuración ---
DATABASE_FILE = "herbie_data.db"
AVR_WIN = 10  # Number of reads to avarage

# Buffer to store data
readings_buffer = []

# --- Serial port config ---
try:
    ser = serial.Serial('/dev/ttyS0', 9600, timeout=1)
    ser.flush()
    print(" Serial port connected. listening for data...")
except serial.SerialException as e:
    print(f"Error in Serial Port: {e}")
    exit()

def calculate_and_save_average(buffer):
    """
    Calculate the avarage of the reading in the buffer and sabes ir in the DB
    Rounded to the fist 2 digits
    """
    valid_moisture = [r['moisture'] for r in buffer if r.get('moisture') is not None]
    valid_temp = [r['temperature'] for r in buffer if r.get('temperature') is not None]
    valid_humidity = [r['humidity'] for r in buffer if r.get('humidity') is not None]
    valid_light = [r['light'] for r in buffer if r.get('light') is not None]

    avg_moisture = round(sum(valid_moisture) / len(valid_moisture), 2) if valid_moisture else None
    avg_temp = round(sum(valid_temp) / len(valid_temp), 2) if valid_temp else None
    avg_humidity = round(sum(valid_humidity) / len(valid_humidity), 2) if valid_humidity else None
    avg_light = round(sum(valid_light) / len(valid_light), 2) if valid_light else None

    average_data = {
        "moisture": avg_moisture,
        "temperature": avg_temp,
        "humidity": avg_humidity,
        "light": avg_light
    }
    
    insert_reading(average_data)
    
def insert_reading(data):
    """
    Conncets to the DB and adds a new reading
    """
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        cursor = conn.cursor()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute("""
        INSERT INTO readings (timestamp, moisture, temperature, humidity, light)
        VALUES (?, ?, ?, ?, ?)
        """, (now, data.get("moisture"), data.get("temperature"), data.get("humidity"), data.get("light")))

        conn.commit()
        conn.close()
        print(f"Average saved in the DB: {data}")

    except sqlite3.Error as e:
        print(f" Error in the Data Base: {e}")

def main():
    """
    Main loop to listen to data, acumulate and avarage
    """
    while True:
        try:
            if ser.in_waiting > 0:
                line_bytes = ser.readline()
                json_string = line_bytes.decode('utf-8').rstrip()
                data = json.loads(json_string)
                
                print(f"  -> Read received: {data}")
                
                # Adds new read to the buffer
                readings_buffer.append(data)
                
                # Checks if is able to avarage
                if len(readings_buffer) >= AVR_WIN:
                    print(f" Acumulated {len(readings_buffer)} readings. Calculating avarage... ---")
                    calculate_and_save_average(readings_buffer)
                    
                    # clear the buffer
                    readings_buffer.clear()
                
        except json.JSONDecodeError:
            print(f"Error in JSON: {json_string}")
        except KeyboardInterrupt:
            print("\nStoped by user")
            break
        except Exception as e:
            print(f"Unexpected error: {e}")
            time.sleep(2)

# --- Main loop ---
if __name__ == "__main__":
    main()
