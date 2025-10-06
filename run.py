from flask import Flask
from app.main.routes import main

def create_app():
    app = Flask(
        __name__,
        template_folder="app/templates",
        static_folder="app/static"
    )
    app.secret_key = "dev-secret"
    app.register_blueprint(main)
    # app.config["EXPLAIN_TEMPLATE_LOADING"] = True  # útil para depurar carga de templates
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)