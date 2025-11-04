# plant_status.py
"""
Saves data read from sensors and las command sended to pico
Uses Thread-safe to share state safely
"""
import threading

# --- Sensors read ---
_latest_average_data = {
    'timestamp': None, 'moisture': None, 'temperature': None, 
    'humidity': None, 'light': None, 'state': None
}
_data_lock = threading.Lock()

def get_latest_data():
    """Get data from last read"""
    with _data_lock:
        return _latest_average_data.copy()

def update_latest_data(new_data_dict):
    """Updates de data dict"""
    global _latest_average_data
    with _data_lock:
        _latest_average_data = new_data_dict

# --- Current command to the pico---
_current_state_on_pico = None
_state_lock = threading.Lock()

def get_pico_state():
    """Gets last command send to pico"""
    with _state_lock:
        return _current_state_on_pico

def set_pico_state(new_state):
    """Updates las state send to the Pico"""
    global _current_state_on_pico
    with _state_lock:
        _current_state_on_pico = new_state