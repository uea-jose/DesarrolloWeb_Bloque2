from flask import request, render_template, redirect, url_for, flash, session
from . import auth_bp
import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash
from app.main.db import get_conn

DEFAULT_USERNAME = "jvilar"
DEFAULT_PASSWORD = "jvilar"

def ensure_user_table_and_default():
    """Create/upgrade usuarios table and ensure default admin user exists."""
    conn = get_conn(); conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # 1) Crear tabla si no existe (schema nuevo)
    cur.execute(
        """CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username   TEXT NOT NULL UNIQUE,
            pass_hash  TEXT,
            nombre     TEXT,
            rol        TEXT NOT NULL DEFAULT 'admin',
            password   TEXT,
            creado_en  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )"""
    )

    # 2) Auto-migración: agregar columnas faltantes
    cols = {r[1] for r in cur.execute("PRAGMA table_info(usuarios)").fetchall()}
    if "pass_hash" not in cols:
        cur.execute("ALTER TABLE usuarios ADD COLUMN pass_hash TEXT")
    if "rol" not in cols:
        cur.execute("ALTER TABLE usuarios ADD COLUMN rol TEXT NOT NULL DEFAULT 'admin'")

    # 3) Backfill: si existe columna legacy 'password' con valores, migrar a pass_hash
    if "password" in cols:
        cur.execute("""SELECT id, password FROM usuarios
                       WHERE (pass_hash IS NULL OR pass_hash='')
                         AND password IS NOT NULL AND password<>''""")
        for row in cur.fetchall():
            cur.execute("UPDATE usuarios SET pass_hash=? WHERE id=?",
                        (generate_password_hash(row["password"]), row["id"]))

    # 4) Asegurar usuario por defecto
    cur.execute("SELECT * FROM usuarios WHERE lower(username)=lower(?)", (DEFAULT_USERNAME,))
    u = cur.fetchone()
    if u is None:
        cur.execute(
            "INSERT INTO usuarios(username, pass_hash, nombre, rol) VALUES(?,?,?,?)",
            (DEFAULT_USERNAME, generate_password_hash(DEFAULT_PASSWORD), "JVilar", "admin")
        )
    else:
        keys = set(u.keys())
        if ("pass_hash" in keys) and (u["pass_hash"] is None or u["pass_hash"] == ""):
            cur.execute("UPDATE usuarios SET pass_hash=? WHERE id=?",
                        (generate_password_hash(DEFAULT_PASSWORD), u["id"]))

    conn.commit()
    conn.close()

def get_user_by_username(username: str):
    conn = get_conn(); conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM usuarios WHERE lower(username) = lower(?)", (username.strip(),))
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None

@auth_bp.route("/login", methods=["GET","POST"])
def login():
    ensure_user_table_and_default()

    if request.method == "POST":
        username = (request.form.get("username") or "").strip().lower()
        password = request.form.get("password") or ""

        user = get_user_by_username(username)

        # Esquema legacy sin pass_hash: migrar on-the-fly para este usuario
        if user and ("pass_hash" not in user or not user["pass_hash"]):
            legacy_plain = user.get("password") or ""
            if legacy_plain:
                conn = get_conn()
                conn.execute("UPDATE usuarios SET pass_hash=? WHERE id=?",
                             (generate_password_hash(legacy_plain), user["id"]))
                conn.commit(); conn.close()
                user = get_user_by_username(username)

        if not user or not user.get("pass_hash") or not check_password_hash(user["pass_hash"], password):
            flash("Usuario o contraseña inválidos.", "danger")
            return redirect(url_for("auth.login"))

        # Sesión
        session["user_id"] = user["id"]
        session["user_username"] = user["username"]
        session["user_nombre"] = user.get("nombre") or user["username"]
        session["user_rol"] = user.get("rol") or "admin"

        # Token por pestaña (WID)
        import secrets
        session["wid"] = secrets.token_urlsafe(16)

        flash("Bienvenido.", "success")
        # Redirigir con WID
        return redirect(url_for("admin.dashboard", wid=session["wid"]))

    return render_template("auth/login.html")

@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("Sesión cerrada.", "info")
    return redirect(url_for("auth.login"))
