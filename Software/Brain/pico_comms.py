# pico_comms.py
"""Manage comunication with Raspberry pico"""

import serial
import json
import time
import config_loader
import plant_status
import plant_logic

ser = None  # Serial object
_readings_buffer = [] # Read Buffer

def init_serial():
    """Opens and configure serial port"""
    global ser
    config = config_loader.get_config()
    try:
        ser = serial.Serial(
            config.get('SERIAL_PORT', '/dev/ttyS0'),
            config.get('BAUD_RATE', 9600),
            timeout=0.1
        )
        ser.flush()
        print("Serial port connected")
        return True
    except serial.SerialException as e:
        print(f"Fatal ERROR using serial port: {e}")
        return False

def close_serial():
    """Closes serial port"""
    if ser and ser.is_open:
        ser.close()
        print("Serial port closed")

def _send_json_command(command_dict):
    """Function to send JSON command"""
    try:
        if ser:
            command_json = json.dumps(command_dict) + '\n'
            ser.write(command_json.encode('utf-8'))
            print(f"Comand: {command_json.strip()}")
        else:
            print("Unable to send command: Serial port busy")
    except Exception as e:
        print(f"ERROR in serial port: {e}")

def send_state_command(state_name):
    """Sends command to Pico"""
    state_name = state_name.upper()
    last_state = plant_status.get_pico_state()
    if state_name != last_state:
        _send_json_command({"command": "set_state", "type": state_name})
        plant_status.set_pico_state(state_name)

def send_volume(volume_level):
    """Send new volume value (0.0 a 1.0)"""
    _send_json_command({"command": "set_volume", "value": volume_level})

def send_brightness(brightness_level):
    """Send new brightness value (0.0 a 1.0)"""
    _send_json_command({"command": "set_brightness", "value": brightness_level})

def serial_listener_loop():
    """Main loop for reader. Reads data and runs logic"""

    global _readings_buffer
    print("Reading thread: STARTING...")
    
    while True:
        config = config_loader.get_config()
        avr_win = config.get('AVR_WIN', 5)
        line_processed = False
        try:
            if ser and ser.in_waiting > 0:
                line_bytes = ser.readline()
                if line_bytes:
                    line_processed = True
                    json_string = line_bytes.decode('utf-8', errors='ignore').strip()
                    if json_string and json_string.startswith('{') and json_string.endswith('}'):
                        try:
                            data = json.loads(json_string)
                            _readings_buffer.append(data)
                            buffer_count = len(_readings_buffer)
                            # print(f"Lectura Recibida ({buffer_count}/{avr_win})") # Opcional

                            if buffer_count >= avr_win:
                                plant_logic.calculate_and_update_average(_readings_buffer)
                                _readings_buffer.clear()
                                
                        except json.JSONDecodeError:
                            print(f"Reading thread: Error JSON {json_string}")
                    # elif json_string:
                         # print(f"Hilo Lector: Recibido no-JSON: {json_string}") # Opcional
        except Exception as e:
            print(f"Reading thread: Error {e}")
            time.sleep(1) # Prevents infinite error loop

        if not line_processed:
            time.sleep(0.1) 
        else:
             time.sleep(0.01)