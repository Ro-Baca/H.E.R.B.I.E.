# config_loader.py

"""
Loads the config values from JSON file
"""

import json
import threading
import plant_database

CONFIG_FILE_PATH = 'config.json'

_config_data = {}
_active_thresholds = {}
_config_lock = threading.Lock()

def _reload_active_thresholds():
    """Function to load the treshold profiles"""
    global _active_thresholds
    profile_name = _config_data.get("selected_plant_profile", "Default")
    _active_thresholds = plant_database.get_profile(profile_name)
    print(f"Plant profile reloaded: {profile_name}")

def load_config():
    """Loads config file and plat profile"""
    global _config_data
    with _config_lock:
        try:
            with open(CONFIG_FILE_PATH, 'r') as f:
                _config_data = json.load(f)
            print("Configuration values loaded")
        except Exception as e:
            print(f"ERROR loading config data, will use default values: {e}")
            _config_data = {
                "selected_plant_profile": "Default", "buzzer_volume": 0.5, "led_brightness": 0.5,
                "AVR_WIN": 5, "SERIAL_PORT": "/dev/ttyS0", "BAUD_RATE": 9600
            }
        
        _reload_active_thresholds()

def get_config():
    """Gets a copy of config.json"""
    with _config_lock:
        return _config_data.copy()

def get_thresholds():
    """Get theshold values from active profile"""
    with _config_lock:
        return _active_thresholds.copy()

def save_config(new_config_data):
    """Saves the new config values in the JSON file"""
    global _config_data
    with _config_lock:
        try:
            # Writes the config dict
            with open(CONFIG_FILE_PATH, 'w') as f:
                json.dump(new_config_data, f, indent=2)
            
            # Reload data in memory 
            _config_data = new_config_data
            _reload_active_thresholds() 
            print(f"New configuration savde")
            return True
        except Exception as e:
            print(f"ERROR saving config values: {e}")
            return False

# --- Initial load---
load_config()