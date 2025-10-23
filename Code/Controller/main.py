# main.py
import time
import hrb_config        # Import general configuration
import hrb_sensors       # Import sensors module
import hrb_communication # Import communication module
    
def main():
    print("Starting system...")
    hrb_config.pwr_led.value(1) # Led to know power on
    
    time.sleep(hrb_config.init_delay) # Warmup for sensors
    
    hrb_sensors.init_sensors() # Starting sensors
    
    try:        
        while True:
            # -- Read sensors data --
            moist_sensor_data = hrb_sensors.get_moist() # Measure moisture
            temp_sensor_data, humid_sensor_data = hrb_sensors.get_temp() # Measure Temperature & Humidity
            light_sensor_data = hrb_sensors.get_light() # Measure light
            
            # -- Send data using Serial port --
            hrb_communication.send_data(moist_sensor_data,temp_sensor_data,humid_sensor_data, light_sensor_data)
            
            # -- Sleep --
            time.sleep(hrb_config.sleep_interval)
            
    except KeyboardInterrupt:
        print("System stop")
    finally:
        print("System off...")
        hrb_config.pwr_led.value(0)
        
    
# --- Start main ---
if __name__ == "__main__":
    main()
