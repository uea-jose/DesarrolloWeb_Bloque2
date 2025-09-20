from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from . import auth_bp
from ..models import Usuario
from ..db import get_user_by_usuario, insert_user

@auth_bp.get("/login")
def login():
    if current_user.is_authenticated:
        return redirect(url_for("auth.dashboard"))
    return render_template("login.html")

@auth_bp.post("/login")
def login_post():
    usuario = request.form.get("usuario", "").strip()
    password = request.form.get("password", "").strip()

    if not usuario or not password:
        flash("Usuario y contraseña son obligatorios", "warning")
        return redirect(url_for("auth.login"))

    row = get_user_by_usuario(usuario)
    if not row or not check_password_hash(row["password"], password):
        flash("Credenciales inválidas", "danger")
        return redirect(url_for("auth.login"))

    user = Usuario(row["id"], row["usuario"], row["password"], row.get("rol"))
    login_user(user)
    flash("Has iniciado sesión", "success")
    return redirect(url_for("auth.dashboard"))

@auth_bp.get("/registro")
def registro():
    if current_user.is_authenticated:
        return redirect(url_for("auth.dashboard"))
    return render_template("register.html")

@auth_bp.post("/registro")
def registro_post():
    usuario = request.form.get("usuario", "").strip()
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "").strip()
    password2 = request.form.get("password2", "").strip()   # ✅ nuevo

    if not usuario or not password:
        flash("Usuario y contraseña son obligatorios", "warning")
        return redirect(url_for("auth.registro"))

    # ✅ validación servidor: contraseñas iguales
    if password != password2:
        flash("Las contraseñas no coinciden", "danger")
        return redirect(url_for("auth.registro"))

    if get_user_by_usuario(usuario):
        flash("El usuario ya existe. Elige otro.", "warning")
        return redirect(url_for("auth.registro"))

    # (Opcional) más reglas de seguridad:
    # if len(password) < 8: ...
    # if not any(c.isdigit() for c in password): ...

    hashed = generate_password_hash(password)
    _id = insert_user(usuario, email, hashed)
    flash("Usuario registrado. Ahora inicia sesión", "success")
    return redirect(url_for("auth.login"))

@auth_bp.get("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")

@auth_bp.route("/logout", methods=["GET", "POST"], endpoint="logout")
@login_required
def logout():
    logout_user()
    flash("Sesión cerrada", "info")
    return redirect(url_for("auth.login"))
