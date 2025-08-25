from flask import Flask, render_template, request

app = Flask(__name__)

# Ruta principal
@app.route("/")
def index():
    return render_template("index.html", title="Inicio")

# Ruta "Acerca de"
@app.route("/about")
def about():
    return render_template("about.html", title="Acerca de")

# Ruta "Contacto" con POST y GET
@app.route("/contacto", methods=["GET", "POST"])
def contacto():
    if request.method == "POST":
        # Aquí podrías capturar los datos del formulario si quieres
        username = request.form.get("username")
        password = request.form.get("password")
        # Por ahora solo los imprimimos en consola (opcional)
        print(f"Usuario: {username}, Contraseña: {password}")
    return render_template("contacto.html", title="Contacto")


if __name__ == "__main__":
    app.run(debug=True)

