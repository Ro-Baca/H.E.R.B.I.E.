# hrb_sensors.py

from machine import ADC, Pin, SoftI2C
from dht import DHT11, InvalidPulseCount
from bh1750 import BH1750
import hrb_config

# --- Initiailzing sensors ---
mois_sens = None
temp_sensor = None
light_sensor = None

# --- Sensor functions ---
def init_sensors():
    """
    Initialization function
    """
    global mois_sens, temp_sensor, light_sensor # Use global values
    print("Booting sensors...")
    
    mois_sens = ADC(Pin(hrb_config.moist_pin))
    print("Moist sensor set")
    temp_sensor = DHT11(Pin(hrb_config.temp_pin))
    print("DHT11 sensor set")
    
    try:
        i2c = SoftI2C(scl=Pin(hrb_config.i2c_scl_pin), sda=Pin(hrb_config.i2c_sda_pin), freq=400000)
        light_sensor = BH1750(bus=i2c, addr=0x23)
        
        print("BH1750 sensor set")
    except Exception as e:
        print(f"Error BH1750: {e}")
    
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

def get_light():
    if light_sensor is None: return None
    try:
        # Readings in Lux
        lux = light_sensor.luminance(BH1750.CONT_HIRES_1)
        return lux
    except Exception as e:
        print(f"Error BH1750: {e}")
        return None