# main.py

import time
import ujson

import hrb_config as config
import hrb_sensors as sensors
import hrb_communication as communication
import hrb_actuators as actuators

def process_command(command_line):
    """
    Process the command from the Pi Zero
    """
    try:
        data = ujson.loads(command_line)
        print(f"Command: {data}")
        
        if data.get("command") == "set_state":
            state_type = data.get("type") # Ej: "DRY", "HOT", etc.
            
            # Search state in the map and runs
            if state_type in actuators.state_map:
                actuators.state_map[state_type]() 
            else:
                print(f"Error: State '{state_type}' not defined.")
                
    except (ValueError, TypeError):
        print(f"Error: JSON command not recognized: {command_line}")

def main():
    """
    Main function
    """
    print("Start HERBIE...")
    
    # Estabilization time
    time.sleep(config.init_delay)
    
    # Initializating hardware
    sensors.init_sensors()
    actuators.init_actuators()
    
    try:
        # actuators.run_state_startup()
        
        while True:
            # Read sensors
            moist_data = sensors.get_moist()
            temp_data, humid_data = sensors.get_temp()
            light_data = sensors.get_light()

            # If moist sensor fails
            if moist_data is None: moist_data = 0.0
            
            # Send data
            communication.send_data(moist_data, temp_data, humid_data, light_data)
            
            # Listen for command in the Zero
            if config.uart.any(): # Data in the buffer
                command_line = config.uart.readline()
                if command_line:
                    process_command(command_line)
            
            time.sleep(config.sleep_interval)
            
    except KeyboardInterrupt:
        print("\nUser stop.")
    finally:
        print("System shutdown...")
        #actuators.run_state_shutdown()
        
# Script start
if __name__ == "__main__":
    main()