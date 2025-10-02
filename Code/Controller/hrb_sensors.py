# hrb_sensors.py

from machine import ADC, Pin
from dht import DHT11, InvalidPulseCount
import hrb_config

# --- Initiailzing sensors ---
mois_sens = None
temp_sensor = None

# --- Sensor functions ---
def init_sensors():
    """
    Initialization function
    """
    global mois_sens, temp_sensor # Use global values
    print("Initialization sensors...")
    mois_sens = ADC(Pin(hrb_config.moist_pin))
    temp_sensor = DHT11(Pin(hrb_config.temp_pin))
    print("Sensors ready")

def get_moist():
    """
    Reads the moisture sensor YL-69 value, calculates a percentage and returns te value
    """
    
    moisture_read = mois_sens.read_u16() # Reading moisture sensor value (16- bit)
    val_range = hrb_config.val_dry - hrb_config.val_mois # Calculate percentage
    if val_range <= 0: return 0.0 # Special case if 0
    sens_read = moisture_read - hrb_config.val_mois
    moist_sensor_data = 100 - (sens_read * 100 / val_range)
    return max(0.0, min(100.0, moist_sensor_data)) # Keep % between 0 and 100

def get_temp():
    """
    Reads the temperature sensor DHT11, sometime the sensor fails so it must manage this
    """
    try:
        temp_sensor.measure() # Reads the sensor using library
        return (temp_sensor.temperature, temp_sensor.humidity) # Returns temperature and humidity values   
    except (OSError, InvalidPulseCount) as e:
        return (None, None) # Returns None for errors
