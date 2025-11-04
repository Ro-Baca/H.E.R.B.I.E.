# plant_logic.py
"""Logic to proccess sensor data"""

import time
import config_loader  
import plant_status

def determine_plant_state(avg_moisture, avg_temp, avg_light):
    """Determine the plant state using avarage readings"""

    thresholds = config_loader.get_thresholds()

    if avg_moisture is None or avg_moisture == 0:
        return "DEAD"
    if avg_moisture < thresholds.get("MIN_MOISTURE", 10):
        return "DRY"
    if avg_temp is not None:
        if avg_temp > thresholds.get("MAX_TEMP", 50):
            return "HOT"
        if avg_temp < thresholds.get("MIN_TEMP", 15):
            return "COLD"
    if avg_light is not None:
        if avg_light < thresholds.get("MIN_LIGHT", 50):
            return "SAD" 
        if avg_light > thresholds.get("MAX_LIGHT", 1000):
            return "TIRED"
    return "OK"

def calculate_and_update_average(buffer):
    """Calculates the average data and updates global state"""
    # --- Avarage ---
    valid_moisture = [r['moisture'] for r in buffer if r.get('moisture') is not None]
    valid_temp = [r['temperature'] for r in buffer if r.get('temperature') is not None]
    valid_humidity = [r['humidity'] for r in buffer if r.get('humidity') is not None]
    valid_light = [r['light'] for r in buffer if r.get('light') is not None]

    avg_moisture = round(sum(valid_moisture) / len(valid_moisture), 2) if valid_moisture else None
    avg_temp = round(sum(valid_temp) / len(valid_temp), 2) if valid_temp else None
    avg_humidity = round(sum(valid_humidity) / len(valid_humidity), 2) if valid_humidity else None
    avg_light = round(sum(valid_light) / len(valid_light), 2) if valid_light else None

    # --- Logic for automatic state ---
    current_state = determine_plant_state(avg_moisture, avg_temp, avg_light)

    average_data_readings = {
        "moisture": avg_moisture, "temperature": avg_temp,
        "humidity": avg_humidity, "light": avg_light,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "state": current_state
    }
    
    # Updates plant status
    plant_status.update_latest_data(average_data_readings)

    # print(f"--- Datos promediados. Estado: {current_state} ---") # Opcional