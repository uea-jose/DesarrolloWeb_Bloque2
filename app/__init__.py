# app/__init__.py
import os
from datetime import timedelta

from dotenv import load_dotenv
from flask import Flask, render_template, redirect, url_for, request, session
from flask_login import LoginManager, UserMixin, current_user

from .db import init_db, get_user_by_id

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-key")

    # Cookies / sesión + no-cache
    app.config.update(
        SESSION_COOKIE_HTTPONLY=True,
        REMEMBER_COOKIE_DURATION=timedelta(days=int(os.getenv('REMEMBER_COOKIE_DURATION_DAYS', '14'))),
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=False,               # True en producción con HTTPS
        PERMANENT_SESSION_LIFETIME=timedelta(minutes=10),
        SESSION_REFRESH_EACH_REQUEST=False,
    )

    @app.before_request
    def _session_permanent():
        session.permanent = True

    @app.after_request
    def _no_cache(response):
        if request.endpoint != "static":
            response.headers["Cache-Control"] = (
                "no-store, no-cache, must-revalidate, max-age=0, private"
            )
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        return response

    # DB init
    with app.app_context():
        init_db()

    # Flask-Login
    login_manager = LoginManager(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message_category = "warning"

    class User(UserMixin):
        def __init__(self, row):
            self.id = str(row["id"])
            self.usuario = row.get("usuario")
            self.rol = row.get("rol", "cliente")
            self.activo = row.get("activo", 1)

        def is_active(self):
            return bool(self.activo)

    @login_manager.user_loader
    def load_user(user_id: str):
        row = get_user_by_id(user_id)
        return User(row) if row else None

    # Blueprints
    from .auth import auth_bp
    app.register_blueprint(auth_bp)

    # Productos/CRUD
    from .products import products_bp
    app.register_blueprint(products_bp)

    from .shop import shop_bp
    app.register_blueprint(shop_bp)

    # Rutas
    @app.route("/", endpoint="index")
    def index():
        # Si hay sesión → dashboard; si no → login
        if current_user.is_authenticated:
            return redirect(url_for("auth.dashboard"))
        return redirect(url_for("auth.login"))

    # Landing/tienda que usa templates/index.html (UN SOLO endpoint)
    @app.route("/tienda", endpoint="tienda")
    def tienda_landing():
        return render_template("index.html")

    # (Opcional) Alias /index también muestra la landing
    @app.route("/index", endpoint="index_page")
    def index_page():
        return render_template("index.html")



    # Alias legado: /dashboard/tienda -> /dashboard/productos/listar
    def _dashboard_tienda():
        return redirect(url_for('shop.home'))
    app.add_url_rule('/dashboard/tienda', endpoint='dashboard_tienda', view_func=_dashboard_tienda)

    return app
