# app/__init__.py
from flask import Flask
from app.main import main_bp

def create_app():
    # Usa rutas por defecto: templates/ y static/ relativas a app.root_path
    app = Flask(__name__)
    app.secret_key = "dev-secret"
    app.register_blueprint(main_bp)
    return app