from flask import Flask, redirect, url_for, session
from app.main import main_bp
from app.auth import auth_bp
from app.admin import admin_bp

def create_app():
    app = Flask(__name__)
    app.secret_key = "dev-secret"

    # Registrar blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(admin_bp, url_prefix="/admin")

    # Middleware de seguridad: obliga a Login
    @app.before_request
    def require_login():
        from flask import request
        allowed_routes = ["auth.login", "auth.logout", "static"]  # rutas que no requieren login
        if (
            "user_id" not in session and
            request.endpoint not in allowed_routes
        ):
            return redirect(url_for("auth.login"))

    return app
