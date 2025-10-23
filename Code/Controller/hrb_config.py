# hrb_config.py

from machine import Pin, ADC, UART

# --- Pins ---
# Sensors
temp_pin = 16
moist_pin = 26
i2c_scl_pin = 8
i2c_sda_pin = 9
# Actuators
buzzer_pin = 14
led_data_pin = 18


# --- Constants ---
init_delay = 2 # initial sensor warm-up time
sleep_interval = 1 # interval between reads
led_count = 8 # actuator leds

# --- Calibration values ---
val_dry = 53437  # Value obtained with the sensor dry
val_mois = 40105 # Value obtained with the sensor in water

# --- Hardware ---
uart = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1))
