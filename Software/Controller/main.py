# main.py (Pico)
import time
import ujson

import hrb_config as config
import hrb_sensors as sensors
import hrb_communication as communication
import hrb_actuators as actuators

def process_command(command_line):
    """
    Process command from Pi Zero
    """
    try:
        data = ujson.loads(command_line)
        print(f"Command: {data}")
        
        command = data.get("command")

        if command == "set_state":
            state_type = data.get("type") # Ej: "DRY", "HOT", etc.
            if state_type in actuators.state_map:
                actuators.state_map[state_type]()  
            else:
                print(f"ERROR: State '{state_type}' not defined.")
        
        
        elif command == "set_volume":
            level = data.get("value") # Float de 0.0 a 1.0
            if level is not None:
                actuators.update_volume(level)
                
        elif command == "set_brightness":
            level = data.get("value") # Float de 0.0 a 1.0
            if level is not None:
                actuators.update_brightness(level)
                
    except (ValueError, TypeError):
        print(f"ERROR: JSON command not recognized: {command_line}")

def main():
    print("Start HERBIE...")
    time.sleep(config.init_delay)
    
    sensors.init_sensors()
    actuators.init_actuators()
    
    try:
        
        while True:
            moist_data = sensors.get_moist()
            temp_data, humid_data = sensors.get_temp()
            light_data = sensors.get_light()

            if moist_data is None: moist_data = 0.0
            
            communication.send_data(moist_data, temp_data, humid_data, light_data)
            
            if config.uart.any():
                command_line = config.uart.readline()
                if command_line:
                    process_command(command_line)
            
            time.sleep(config.sleep_interval)
            
    except KeyboardInterrupt:
        print("\nUser stop.")
    finally:
        print("System shutdown...")
        # actuators.run_state_shutdown() # Opcional, ya que la Zero lo llama

if __name__ == "__main__":
    main()