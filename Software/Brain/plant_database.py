# plant_database.py
"""
Database for plant prfiles
"""

PLANT_PROFILES = {
    "Default": {
        "MIN_MOISTURE": 20.0,
        "MAX_TEMP": 35.0,
        "MIN_TEMP": 15.0,
        "MIN_LIGHT": 200.0,
        "MAX_LIGHT": 2000.0
    },
    "Suculenta": {
        "MIN_MOISTURE": 10.0, 
        "MAX_TEMP": 40.0,     
        "MIN_TEMP": 10.0,
        "MIN_LIGHT": 1500.0,   
        "MAX_LIGHT": 10000.0
    },
    "Helecho": {
        "MIN_MOISTURE": 40.0, 
        "MAX_TEMP": 28.0,      
        "MIN_TEMP": 18.0,
        "MIN_LIGHT": 100.0,    
        "MAX_LIGHT": 1500.0
    },
    "Pothos (Planta de Interior)": {
        "MIN_MOISTURE": 25.0,
        "MAX_TEMP": 30.0,
        "MIN_TEMP": 15.0,
        "MIN_LIGHT": 150.0,
        "MAX_LIGHT": 2000.0
    }
}

def get_available_plants():
    """Retruns a list of profile names"""
    return list(PLANT_PROFILES.keys())

def get_profile(name):
    """Returns a profile from name"""
    return PLANT_PROFILES.get(name, PLANT_PROFILES["Default"])