# app/main/usuarios_routes.py
import os, sqlite3, json, csv, datetime
from flask import render_template, request, redirect, url_for, flash, jsonify
from . import main_bp as main  # mismo blueprint

# ----- Rutas de archivos -----
BASE_DIR  = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATOS_DIR = os.path.join(BASE_DIR, "datos")
DB_DIR    = os.path.join(BASE_DIR, "app", "data")

USU_DB    = os.path.join(DB_DIR, "usuarios.db")
TXT_PATH  = os.path.join(DATOS_DIR, "datos.txt")
CSV_PATH  = os.path.join(DATOS_DIR, "datos.csv")
JSON_PATH = os.path.join(DATOS_DIR, "datos.json")

# ----- Conexión SQLite -----
def get_conn():
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(USU_DB)
    conn.row_factory = sqlite3.Row
    return conn

# ----- Inicialización / migración tabla usuarios -----
def init_user_db():
    os.makedirs(DB_DIR, exist_ok=True)
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre    TEXT NOT NULL,
                email     TEXT NOT NULL,
                edad      INTEGER NOT NULL CHECK(edad >= 0),
                provincia TEXT,
                ciudad    TEXT,
                creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Auto-migración de columnas nuevas
        cols = {r[1] for r in conn.execute("PRAGMA table_info(usuarios)").fetchall()}
        if "provincia" not in cols:
            conn.execute("ALTER TABLE usuarios ADD COLUMN provincia TEXT")
        if "ciudad" not in cols:
            conn.execute("ALTER TABLE usuarios ADD COLUMN ciudad TEXT")
        conn.commit()

# ----- Persistencia adicional a TXT/CSV/JSON -----
def persist_to_files(nombre, email, edad, provincia, ciudad):
    os.makedirs(DATOS_DIR, exist_ok=True)
    ts = datetime.datetime.now().isoformat(timespec="seconds")

    # TXT
    with open(TXT_PATH, "a", encoding="utf-8") as f:
        f.write(f"{nombre},{email},{edad},{provincia},{ciudad},{ts}\n")

    # CSV
    header_needed = not os.path.exists(CSV_PATH) or os.path.getsize(CSV_PATH) == 0
    with open(CSV_PATH, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if header_needed:
            w.writerow(["nombre","email","edad","provincia","ciudad","creado_en"])
        w.writerow([nombre, email, int(edad), provincia, ciudad, ts])

    # JSON
    data = {"usuarios": []}
    if os.path.exists(JSON_PATH) and os.path.getsize(JSON_PATH) > 0:
        try:
            with open(JSON_PATH, "r", encoding="utf-8") as f:
                data = json.load(f) or {"usuarios": []}
        except Exception:
            data = {"usuarios": []}
    data["usuarios"].append({
        "nombre": nombre, "email": email, "edad": int(edad),
        "provincia": provincia, "ciudad": ciudad, "creado_en": ts
    })
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# (opcional) reconstrucción de TXT/CSV/JSON desde la BD
def _rebuild_side_files_from_db():
    os.makedirs(DATOS_DIR, exist_ok=True)
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT nombre, email, edad, provincia, ciudad, creado_en
            FROM usuarios ORDER BY id DESC
        """).fetchall()
        users = [dict(r) for r in rows]

    with open(TXT_PATH, "w", encoding="utf-8") as f:
        for u in users:
            f.write(f"{u['nombre']},{u['email']},{u['edad']},{u.get('provincia','')},{u.get('ciudad','')},{u['creado_en']}\n")

    with open(CSV_PATH, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["nombre","email","edad","provincia","ciudad","creado_en"])
        for u in users:
            w.writerow([u["nombre"], u["email"], int(u["edad"]), u.get("provincia",""), u.get("ciudad",""), u["creado_en"]])

    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump({"usuarios": users}, f, indent=2, ensure_ascii=False)

# Inicializa BD al importar el módulo
init_user_db()

# =================== RUTAS ===================

# Crear / registrar usuario
@main.route("/registrarse", methods=["GET", "POST"])
def registrarse():
    if request.method == "GET":
        # Las plantillas están en templates/main/
        return render_template("main/registrarse.html")

    nombre    = (request.form.get("nombre") or "").strip()
    email     = (request.form.get("email")  or "").strip()
    edad      = (request.form.get("edad")   or "").strip()
    provincia = (request.form.get("provincia") or "").strip()
    ciudad    = (request.form.get("ciudad")    or "").strip()

    if (not nombre or not email or not edad.isdigit() or int(edad) < 0
        or not provincia or not ciudad):
        flash("Completa todos los campos y selecciona provincia/ciudad válidas.", "warning")
        return redirect(url_for("main.registrarse"))

    persist_to_files(nombre, email, edad, provincia, ciudad)

    with get_conn() as conn:
        conn.execute("""
            INSERT INTO usuarios (nombre,email,edad,provincia,ciudad)
            VALUES (?,?,?,?,?)
        """, (nombre, email, int(edad), provincia, ciudad))
        conn.commit()

    flash("Registro exitoso.", "success")
    return redirect(url_for("main.usuarios"))

# Listado
@main.route("/usuarios")
def usuarios():
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT id, nombre, email, edad, provincia, ciudad, creado_en
            FROM usuarios
            ORDER BY id DESC
        """).fetchall()
    usuarios = [dict(r) for r in rows]
    return render_template("main/usuarios_list.html", usuarios=usuarios)

# API JSON
@main.route("/api/usuarios.json")
def api_usuarios():
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT nombre, email, edad, provincia, ciudad, creado_en
            FROM usuarios ORDER BY id DESC
        """).fetchall()
    return jsonify({"usuarios": [dict(r) for r in rows]})

# Editar
@main.route("/usuarios/<int:uid>/editar", methods=["GET", "POST"], endpoint="usuario_edit")
def usuario_edit(uid):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT id, nombre, email, edad, provincia, ciudad FROM usuarios WHERE id=?",
            (uid,)
        ).fetchone()
        if not row:
            flash("Usuario no encontrado.", "warning")
            return redirect(url_for("main.usuarios"))

        if request.method == "POST":
            nombre    = (request.form.get("nombre") or "").strip()
            email     = (request.form.get("email")  or "").strip()
            edad_str  = (request.form.get("edad")   or "0").strip()
            provincia = (request.form.get("provincia") or "").strip()
            ciudad    = (request.form.get("ciudad")    or "").strip()

            if not (nombre and email and provincia and ciudad and edad_str.isdigit()):
                flash("Completa todos los campos correctamente.", "warning")
                return redirect(url_for("main.usuario_edit", uid=uid))

            edad = int(edad_str)
            conn.execute("""
                UPDATE usuarios
                   SET nombre=?, email=?, edad=?, provincia=?, ciudad=?
                 WHERE id=?""",
                (nombre, email, edad, provincia, ciudad, uid)
            )
            conn.commit()
            flash("Usuario actualizado.", "success")
            return redirect(url_for("main.usuarios"))

    return render_template("main/usuarios_form.html", u=dict(row))

# Eliminar
@main.route("/usuarios/<int:uid>/eliminar", methods=["POST"], endpoint="usuario_delete")
def usuario_delete(uid):
    with get_conn() as conn:
        cur = conn.execute("DELETE FROM usuarios WHERE id=?", (uid,))
        conn.commit()
        borrados = cur.rowcount

    # Si quieres sincronizar archivos auxiliares, descomenta:
    # try:
    #     _rebuild_side_files_from_db()
    # except Exception:
    #     pass

    flash("Usuario eliminado." if borrados else "No se encontró el usuario.",
          "info" if borrados else "warning")
    return redirect(url_for("main.usuarios"))
