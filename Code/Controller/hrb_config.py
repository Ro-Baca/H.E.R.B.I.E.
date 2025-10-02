# hrb_config.py

from machine import Pin, ADC, UART

# --- Pins ---
temp_pin = 16
moist_pin = 26
pwr_led_pin = 15

# --- Constants ---
init_delay = 2 # initial sensor warm-up time
sleep_interval = 1 # interval between reads

# --- Calibration values ---
val_dry = 65535  # Value obtained with the sensor dry
val_mois = 19028 # Value obtained with the sensor in water

# --- Hardware ---
uart = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1))
pwr_led = Pin(pwr_led_pin, Pin.OUT)