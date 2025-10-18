from flask import Flask

# Creates an instance of Flask
app = Flask(__name__)

# Defines main rout
@app.route('/')
def index():
    # This function executes and returns the text
    return '<h1>¡Hola, HERBIE!</h1><p>El servidor web está funcionando.</p>'

# Starts the web server
if __name__ == '__main__':
    # host='0.0.0.0' makes the server visibel in the local network
    app.run(host='0.0.0.0', port=5000, debug=True)
