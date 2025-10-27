from flask import Flask, render_template

app = Flask(__name__)

# Datos falsos para probar
fake_data = {
    'timestamp': '2025-10-25 00:00:00', 'moisture': 50.0, 'temperature': 22.5, 
    'humidity': 45.0, 'light': 1000.0
}

@app.route('/')
def index():
    print("--- Ejecutando index() ---") # Mensaje de prueba
    # Pasa datos falsos a la plantilla
    return render_template('debugger.html', data=fake_data) 

if __name__ == '__main__':
    print("🚀 Iniciando servidor Flask simple...")
    app.run(host='0.0.0.0', port=5000, debug=True)