from flask import Flask, render_template
from flask_login import LoginManager
from .db import get_user_by_id
from .models import Usuario
from .db_init import ensure_database_and_tables

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

    # Auto-inicializa la base de datos y tablas al arrancar
    try:
        ensure_database_and_tables(logger=app.logger)
    except Exception as e:
        app.logger.warning(f"DB auto-init skipped or failed: {e}")

    # Inicializa Flask-Login
    login_manager.init_app(app)

    # Registra el blueprint de autenticación
    from .auth import auth_bp
    app.register_blueprint(auth_bp)

    # Context processor opcional
    @app.context_processor
    def inject_globals():
        return {"app_name": "Flask Login"}

    # Ruta raíz → renderiza index.html
    @app.route("/")
    def index():
        return render_template("index.html")

    return app
