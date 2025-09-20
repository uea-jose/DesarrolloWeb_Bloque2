
from flask import Flask, render_template, current_app
from flask_login import LoginManager
from .db import get_user_by_id
from .models import Usuario

login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message_category = "warning"

@login_manager.user_loader
def load_user(user_id: str):
    row = get_user_by_id(user_id)
    if row:
        return Usuario(row["id"], row["usuario"], row["password"], row.get("rol"))
    return None

def create_app(config_object: str = "config.Config"):
    app = Flask(__name__)
    app.config.from_object(config_object)

    # Inicializa Flask-Login
    login_manager.init_app(app)

    # Registra blueprint de autenticación
    from .auth import auth_bp
    app.register_blueprint(auth_bp)

    # Context processor opcional
    @app.context_processor
    def inject_has_endpoint():
        def has_endpoint(name: str) -> bool:
            return name in current_app.view_functions
        return dict(has_endpoint=has_endpoint)

    # Página de inicio
    @app.get("/")
    def index():
        return render_template("index.html")

    return app
