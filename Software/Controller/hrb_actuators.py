# hrb_actuators.py
import machine
import utime
import hrb_config
from ws2812 import WS2812

# --- Configuration Values ---
buzzer_pwm = None
VOLUME = 32768  # 50% by default
BRIGHTNESS = 0.5 # 50% by default

# --- Colors ---
BLACK = [0, 0, 0]
BLACK = [0, 0, 0]
RED, YELLOW, BLUE, ORANGE, MAGENTA, CYAN, GREEN = [BLACK]*7

# --- Config values update ---
def update_volume(level):
    """Updates global volume (0.0 a 1.0)"""
    global VOLUME
    
    VOLUME = int(level * 65535)
    print(f"Volume updated: {level} ({VOLUME})")

def update_brightness(level):
    """Updates flobal brightness and recalculates color"""
    global BRIGHTNESS, RED, YELLOW, BLUE, ORANGE, MAGENTA, CYAN, GREEN
    
    BRIGHTNESS = max(0.0, min(1.0, level)) 
    
    RED = [int(255 * BRIGHTNESS), 0, 0]
    YELLOW = [int(255 * BRIGHTNESS), int(150 * BRIGHTNESS), 0]
    BLUE = [0, 0, int(255 * BRIGHTNESS)]
    ORANGE = [int(255 * BRIGHTNESS), int(60 * BRIGHTNESS), 0]
    MAGENTA = [int(255 * BRIGHTNESS), 0, int(255 * BRIGHTNESS)]
    CYAN = [0, int(255 * BRIGHTNESS), int(255 * BRIGHTNESS)]
    GREEN = [0, int(255 * BRIGHTNESS), 0]
    print(f"Brillo actualizado a {level}")

# --- Initialization ---
def init_actuators():
    """Actuators initialization"""
    global buzzer_pwm, strip
    # Init Buzzer
    try:
        buzzer_pwm = machine.PWM(machine.Pin(hrb_config.buzzer_pin))
        buzzer_pwm.duty_u16(0) # Buzzer off
    except Exception as e:
        print(f"ERROR initializating buzzer: {e}")
    
    # Init NeoPixel
    try:
        strip = WS2812(machine.Pin(hrb_config.led_data_pin), hrb_config.led_count)
        led_turn_off() # Leds off
    except Exception as e:
        print(f"Error initializating NeoPixel: {e}")

    update_brightness(BRIGHTNESS)
    led_turn_off() # Leds off

# --- Hard Stop function
def off():
    """Emergency function for Hard stop"""
    print("Actuators off...")
    actuators.no_tone()
    actuators.led_turn_off()

# --- Sound primitives ---

def set_tone(frequency):
    """Activate buzzer to a specific freq"""
    if buzzer_pwm and frequency > 0:
        buzzer_pwm.freq(frequency)
        buzzer_pwm.duty_u16(VOLUME)
    elif buzzer_pwm:
        buzzer_pwm.duty_u16(0) # Freq 0 is off

def no_tone():
    """Buzzer off"""
    if buzzer_pwm:
        buzzer_pwm.duty_u16(0)

def beep(frequency, duration_ms):
    """Generate a beep"""
    set_tone(frequency)
    utime.sleep_ms(duration_ms)
    no_tone()

def pause(duration_ms):
    """No tone"""
    no_tone()
    utime.sleep_ms(duration_ms)

def sweep(start_freq, end_freq, duration_ms, steps=20):
    """Generate a sweep"""
    if not buzzer_pwm: return
    step_duration = duration_ms // steps
    freq_step = (end_freq - start_freq) / steps
    set_tone(start_freq)
    for i in range(steps):
        current_freq = start_freq + (freq_step * i)
        buzzer_pwm.freq(int(current_freq))
        utime.sleep_ms(step_duration)
    no_tone()

def vibrato(base_freq, offset, cycle_ms, total_duration_ms):
    """Generate a vibrato"""
    if not buzzer_pwm: return
    end_time = utime.ticks_add(utime.ticks_ms(), total_duration_ms)
    while utime.ticks_diff(end_time, utime.ticks_ms()) > 0:
        set_tone(base_freq + offset); utime.sleep_ms(cycle_ms)
        if utime.ticks_diff(end_time, utime.ticks_ms()) <= 0: break
        set_tone(base_freq - offset); utime.sleep_ms(cycle_ms)
    no_tone()

# --- LED Primitives ---

def led_fill(color):
    """Fill strip of a color"""
    if strip:
        for i in range(hrb_config.led_count):
            strip[i] = color
        strip.write()

def led_turn_off():
    """LEDs off"""
    led_fill(BLACK)

def led_startup():
    """Startup sequence"""
    if not strip: return
    for i in range(hrb_config.led_count):
        strip[i] = GREEN
        strip.write()
        utime.sleep_ms(60)

def led_shutdown():
    """Shutdown sequence"""
    if not strip: return
    for i in range(hrb_config.led_count - 1, -1, -1):
        strip[i] = BLACK
        strip.write()
        utime.sleep_ms(60)

def led_shiver(color, cycle_ms, total_duration_ms):
    """
    Blink LEDs altrenated
    """
    if not strip: return
    
    end_time = utime.ticks_add(utime.ticks_ms(), total_duration_ms)
    
    while utime.ticks_diff(end_time, utime.ticks_ms()) > 0:
        
        for i in range(hrb_config.led_count):
            strip[i] = color if i % 2 == 0 else BLACK
        strip.write()
        utime.sleep_ms(cycle_ms)
        
        if utime.ticks_diff(end_time, utime.ticks_ms()) <= 0: break
            
        for i in range(hrb_config.led_count):
            strip[i] = color if i % 2 == 1 else BLACK
        strip.write()
        utime.sleep_ms(cycle_ms)
        
    led_turn_off()

# --- Emotion Functions (Sound and LED) ---

def run_state_dead():
    """EMOTION: DEAD - Red LED still, no sound"""
    print("EMOTION: DEAD")
    no_tone()
    led_fill(RED)
    
def run_state_dry():
    """EMOTION: DRY  - Yellow LED blink slow, low beeping sound"""
    print("EMOTION: DRY")
    for _ in range(3):
        set_tone(1200)
        led_fill(YELLOW)
        utime.sleep_ms(150)
        
        no_tone()
        led_turn_off()
        utime.sleep_ms(50)
        
        set_tone(800)
        led_fill(YELLOW)
        utime.sleep_ms(300)
        
        no_tone()
        led_turn_off()
        utime.sleep_ms(400)
        
    run_state_warning()

def run_state_hot():
    """EMOTION: HOT - Red LED blink slow, low to up sweep and beep"""
    print("EMOTION: HOT")
    
    led_fill(RED)
    sweep(800, 1600, 400)
    led_turn_off()
    pause(100)
    
    set_tone(1500)
    led_fill(RED)
    utime.sleep_ms(200)
    
    no_tone()
    led_turn_off()
    utime.sleep_ms(100)

    set_tone(1500)
    led_fill(RED)
    utime.sleep_ms(200)
    no_tone()
    led_turn_off()
    
    run_state_warning()

def run_state_cold():
    """EMOTION: COLD - Blue LED blinking fast, vibrato low"""
    print("EMOTION: COLD")
    beep(800,100)
    led_shiver(BLUE, 50, 200)
    pause(200)
    vibrato(1000, 100, 70, 400)
    led_shiver(BLUE, 70, 400)
    pause(200)
    vibrato(1000, 100, 70, 400)
    led_shiver(BLUE, 70, 400)
    led_turn_off()
    
    run_state_warning()
    
def run_state_sad():
    """EMOTION: SAD - Magenta LED blinking slow, low beep and sweep low to up."""
    print("EMOTION: SAD")
    for _ in range (2):
        led_fill(MAGENTA)
        beep(800,300)
        sweep(800,1000,100)
        
        led_turn_off() 
        pause(500)
        
    run_state_warning()

def run_state_tired():
    """EMOTION: TIRED - Cyan LED blinking fast, high beep blink"""
    print("EMOTION: TIRED")
    for _ in range(2):
        for _ in range(5):
            led_fill(CYAN)
            set_tone(1200)
            utime.sleep_ms(80)
            no_tone()
            led_turn_off()
            utime.sleep_ms(50)
        pause(120)
        
    run_state_warning()
    
def run_state_ok():
    """EMOTION: OK - Green LED still, no sound"""
    print("EMOTION: OK")
    no_tone()
    led_fill(GREEN)

def run_state_warning():
    """EMOTION: WARNING (NOT OK) - Orange light, no sound """
    print("EMOTION: WARNING")
    led_fill(ORANGE)

def run_state_thanks():
    """EMOTION: THANKS - Cyan and green LED blink slow, high beeps """
    print("EMOTION: THANKS")
    led_fill(CYAN); beep(1000, 300); led_turn_off(); 
    led_fill(CYAN); beep(1200, 200); led_turn_off(); pause(20)
    #led_fill(GREEN); beep(1200, 200);
    run_state_ok()

def run_state_startup():
    """EMOTION: STARTUP - starup sequence"""
    print("EMOTION: STARTUP")
    led_startup()
    beep(1000, 100); sweep(700, 1000, 400); pause(10); beep(1200, 100)
    led_turn_off()

def run_state_shutdown():
    """EMOTION: SHUTDOWN - shutdown sequence"""
    print("EMOTION: SHUTDOWN")
    led_shutdown()
    beep(1200, 100); sweep(1000, 700, 400); pause(10); beep(800, 100); no_tone()
    

# --- Command Mapping ---
state_map = {
    "DEAD": run_state_dead,
    "DRY": run_state_dry,
    "HOT": run_state_hot,
    "COLD": run_state_cold,
    "SAD": run_state_sad,
    "TIRED": run_state_tired,
    "OK": run_state_ok,
    "THANKS": run_state_thanks,
    "WARNING": run_state_warning,
    "STARTUP": run_state_startup,
    "SHUTDOWN": run_state_shutdown,
}