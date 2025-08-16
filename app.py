from flask import Flask

app = Flask(__name__)

# Ruta principal
@app.route('/')
def index():
    return "¡Hola Mundo, Este es mi primer proyecto con Flask!"

# Ruta dinámica
@app.route('/usuario/<nombre>')
def usuario(nombre):
    return f'Bienvenido, {nombre}!'

if __name__ == '__main__':
    app.run(debug=True)
