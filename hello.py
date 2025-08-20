from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/contacto")
def contacto():
    return render_template("contacto.html")

@app.route("/esencias")
def esencias():
    return render_template("Esencias.html")

@app.route("/femeninos")
def femeninos():
    return render_template("femeninos.html")

@app.route("/masculinos")
def masculinos():
    return render_template("masculinos.html")

if __name__ == "__main__":
    app.run(debug=True)
