# app.py
""" Flask runner for web app """

import sys
import time
import threading
from flask import Flask, render_template, request, redirect, url_for, jsonify

import config_loader
import plant_status
import pico_comms
import plant_database

app = Flask(__name__)

# --- Routes ---

@app.route('/')
def index():
    """Main page"""
    current_data = plant_status.get_latest_data()
    thresholds = config_loader.get_thresholds()
    current_config = config_loader.get_config()

    return render_template('inicio.html', 
                           data=current_data, 
                           thresholds=thresholds,
                           config=current_config,
                           active_page='inicio')

@app.route('/stats')
def stats():
    """Statistics Page"""
    return render_template('placeholder.html', 
                           page_title='ESTADISTICAS',
                           active_page='stats')

@app.route('/tips')
def tips():
    """Advice Page"""
    return render_template('placeholder.html', 
                           page_title='CONSEJOS',
                           active_page='tips')

@app.route('/config')
def config_page():
    """Muestra la página de configuración con todos los valores."""
    available_plants = plant_database.get_available_plants()
    current_config = config_loader.get_config()
    
    return render_template('config.html',
                           available_plants=available_plants,
                           current_config=current_config,
                           active_page='config')

@app.route('/save_config', methods=['POST'])
def save_config_route():
    """
    Ruta para guardar la nueva planta, volumen, brillo y freq. de medición.
    """
    try:
        # 1. Carga la config actual para usarla como base
        new_config = config_loader.get_config()
        
        # 2. Obtiene TODOS los valores del formulario
        new_plant = request.form.get('plant_profile')
        new_volume = float(request.form.get('buzzer_volume'))
        new_brightness = float(request.form.get('led_brightness'))
        new_avr_win = int(request.form.get('AVR_WIN')) # <-- NUEVA LÍNEA

        # 3. Valida los valores
        if not (new_plant and new_plant in plant_database.get_available_plants()):
            return "Error: Selección de planta no válida.", 400
        if not (0.0 <= new_volume <= 1.0):
            return "Error: Volumen no válido.", 400
        if not (0.0 <= new_brightness <= 1.0):
            return "Error: Brillo no válido.", 400
        if not (1 <= new_avr_win <= 60): # Límite de 1s a 1 minuto
            return "Error: Frecuencia de medición no válida.", 400
        
        # 4. Actualiza el diccionario de config
        new_config["selected_plant_profile"] = new_plant
        new_config["buzzer_volume"] = new_volume
        new_config["led_brightness"] = new_brightness
        new_config["AVR_WIN"] = new_avr_win # <-- NUEVA LÍNEA

        # 5. Guarda el diccionario actualizado en config.json
        success = config_loader.save_config(new_config)
        
        if success:
            # 6. Envía los nuevos valores de hardware a la Pico
            pico_comms.send_volume(new_volume)
            pico_comms.send_brightness(new_brightness)
            # (No es necesario enviar AVR_WIN a la Pico)
            
            return redirect(url_for('config_page'))
        
        return "Error al guardar el archivo", 500
            
    except Exception as e:
        print(f"Error en /save_config: {e}")
        return str(e), 500

@app.route('/debugger')
def debugger():
    """Debugging page"""
    current_data = plant_status.get_latest_data()
    thresholds = config_loader.get_thresholds()
    return render_template('debugger.html', data=current_data, thresholds=thresholds)

@app.route('/send_command', methods=['POST'])
def handle_command():
    """Debugger function"""
    if request.method == 'POST':
        selected_emotion = request.form.get('emotion')
        if selected_emotion:
            pico_comms.send_state_command(selected_emotion)
    return redirect(url_for('debugger'))

# --- Runs program ---
if __name__ == '__main__':
    # config_loader.load_config() execurtes at import
    
    if not pico_comms.init_serial():
        print("ERROR: Unable to conncet serial port")
        print("Bye...")
        sys.exit(1)

    listener_thread = threading.Thread(target=pico_comms.serial_listener_loop, daemon=True)
    listener_thread.start()

    pico_comms.send_state_command("STARTUP")
    
    # Envía los valores de config a la Pico al iniciar
    config = config_loader.get_config()
    pico_comms.send_volume(config.get('buzzer_volume', 0.5))
    pico_comms.send_brightness(config.get('led_brightness', 0.5))
    
    #print(f"Iniciando servidor web en http://0.0.0.0:5000")
    
    try:
        app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
    except KeyboardInterrupt:
        print("\nClosing web server...")
    finally:
        pico_comms.send_state_command("SHUTDOWN")
        time.sleep(1) 
        pico_comms.close_serial()