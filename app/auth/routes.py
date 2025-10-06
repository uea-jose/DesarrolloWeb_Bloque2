import re
from functools import wraps
from flask import (
    render_template, request, redirect, url_for, flash,
    make_response, session, current_app
)
from flask_login import login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
from . import auth_bp
from ..db import get_user_by_usuario, insert_user

def _valid_user(u: str) -> bool:
    return bool(re.fullmatch(r"[A-Za-z0-9_.-]{3,30}", u or ""))

def _valid_password(p: str) -> bool:
    return bool(len(p or "") >= 8 and re.search(r"[a-z]", p) and re.search(r"[A-Z]", p) and re.search(r"\d", p))


# === utilidades de no-cache ===
def _nocache_headers(resp):
    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0, private"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Expires"] = "0"
    return resp

def nocache(view):
    @wraps(view)
    def _wrapped(*args, **kwargs):
        resp = make_response(view(*args, **kwargs))
        return _nocache_headers(resp)
    return _wrapped

def redirect_nocache(location):
    resp = make_response(redirect(location))
    return _nocache_headers(resp)

# === modelo de sesión ===
class _U(UserMixin):
    def __init__(self, row):
        self.id = str(row["id"])
        self.usuario = row.get("usuario")
        self.rol = row.get("rol", "cliente")
        self.activo = row.get("activo", 1)
    def is_active(self):
        return bool(self.activo)

@auth_bp.route("/login", methods=["GET", "POST"], endpoint="login")
@nocache
def login():
    if current_user.is_authenticated and request.method == "GET":
        return redirect_nocache(url_for("auth.dashboard"))

    if request.method == "POST":
        usuario  = (request.form.get("usuario") or "").strip()
        password = request.form.get("password") or ""
        row = get_user_by_usuario(usuario)
        remember = bool(request.form.get('remember'))
        if not row:
            flash("Usuario no encontrado.", "danger")
        elif not check_password_hash(row["password"], password):
            flash("Contraseña incorrecta.", "danger")
        else:
            # No persistimos cookie de “recordarme”
            login_user(_U(row), remember=remember, fresh=True)
            flash(f"¡Bienvenido, {row.get('usuario')}!", "success")
            next_url = request.args.get("next") or request.form.get("next")
            if next_url and next_url.startswith("/"):
                return redirect_nocache(next_url)
            return redirect_nocache(url_for("auth.dashboard"))

    return render_template("login.html")

@auth_bp.route("/register", methods=["GET", "POST"], endpoint="register")
@nocache
def register():
    if request.method == "POST":
        usuario  = (request.form.get("usuario") or "").strip()
        password = request.form.get("password") or ""
        password2= request.form.get("password2") or ""
        if not _valid_user(usuario):
            flash("Usuario inválido. Usa 3-30 caracteres: letras, números, _ . -", "warning")
        elif not _valid_password(password):
            flash("La contraseña debe tener mínimo 8 caracteres, con mayúsculas, minúsculas y números.", "warning")
        elif password != password2:
            flash("Las contraseñas no coinciden.", "warning")
        elif get_user_by_usuario(usuario):
            flash("Ese usuario ya existe.", "warning")
        else:
            insert_user(usuario, generate_password_hash(password), rol="cliente", activo=1)
            flash("Registro correcto. Inicia sesión.", "success")
            return redirect_nocache(url_for("auth.login"))
    return render_template("register.html")

@auth_bp.get("/dashboard")
@login_required
@nocache
def dashboard():
    return render_template("dashboard.html")

@auth_bp.get("/logout")
@login_required
def logout():
    logout_user()
    flash("Sesión cerrada.", "info")
    # Nota: si quisieras borrar la cookie de sesión explícitamente,
    # perderías el flash anterior. Para mantener el flash, devolvemos
    # un redirect no-cache y dejamos que Flask regenere la cookie vacía.
    return redirect_nocache(url_for("auth.login"))
