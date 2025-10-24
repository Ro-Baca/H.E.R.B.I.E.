# pico_tester.py

import serial
import time
import json
import threading
import sys

# --- Serial port config ---
try:
    ser = serial.Serial('/dev/ttyS0', 9600, timeout=1)
    ser.flush()
    print("Serial port connected")
except serial.SerialException as e:
    print(f"Error in serial port: {e}")
    exit()

def send_state_command(state_name):
    """ Set and send a command to the Pico"""
    
    state_name = state_name.upper() # Only capital letters
    
    # {"command": "set_state", "type": "EMOTION"}
    command_json = f'{{"command": "set_state", "type": "{state_name}"}}\n'
    
    print(f"\r[...Enviando comando: {command_json.strip()}]")
    ser.write(command_json.encode('utf-8')) # Sends command

# --- Threads ---
def serial_reader_thread():
    """
    Thread to excecute in parallel, listen
    constatnrly to the Pico 
    """
    while True:
        try:
            if ser.in_waiting > 0:
                line_bytes = ser.readline()
                json_string = line_bytes.decode('utf-8').rstrip()
                
                if json_string: 
                    data = json.loads(json_string)
                    
                    # \r goes to the start of the line
                    # " " * 40 cleans the text
                    # \n jumps to next line
                    print(f"\r[PICO -> YOU]: {data}" + " " * 40 + "\n", end="")
                    
                    # shows user prompt
                    print(f"[YOU -> PICO]: ", end="")
                    sys.stdout.flush() # Forces prompt print

        except json.JSONDecodeError:
            print(f"\r‼️ Error in JSON: {json_string}\n[YOU-> PICO]: ", end="")
            sys.stdout.flush()
        except Exception as e:
            print(f"\r‼️ Error Thread: {e}\n[YOU -> PICO]: ", end="")
            sys.stdout.flush()
        
        time.sleep(0.1) # to not overload CPU

def main():
    """
    Main thread. receibes the commands 
    from the user
    """
    
    # Start second thread
    # daemon=True will shut down the thread when script is exit
    reader_thread = threading.Thread(target=serial_reader_thread, daemon=True)
    reader_thread.start()

    # Instructions
    print("--- H.E.R.B.I.E. ---")
    print("Write a Emotion (ej: 'HOT', 'DRY', 'OK') and press enter to send.")
    print("Ctrl+C to exit")
    print(f"[YOU-> PICO]: ", end="")
    
    try:
        # loop to read input
        while True:
            command_to_send = input()
            
            if command_to_send:
                send_state_command(command_to_send)
                print(f"[YOU -> PICO]: ", end="") # Shows prompt

    except KeyboardInterrupt:
        print("\nEXIT...")
    finally:
        ser.close()
        print("Serial port closed. BYE.")

# --- Script start point ---
if __name__ == "__main__":
    main()