# app/main/routes.py
from flask import render_template, request, redirect, url_for, flash, make_response
from .db import get_conn, init_db
from . import main_bp as main  # mismo blueprint

# ---------- Helper para render con no-cache ----------
def render_page(template_path: str, **context):
    resp = make_response(render_template(template_path, **context))
    resp.headers["Cache-Control"] = "no-store"
    return resp

# --------- Páginas del sitio ---------
@main.route("/")
def index():
    """Home: destacados y recientes."""
    conn = get_conn(); cur = conn.cursor()
    try:
        # Destacados por stock
        cur.execute("""
            SELECT id,nombre,tipo,precio,stock
            FROM productos
            ORDER BY stock DESC, id DESC
            LIMIT 4
        """)
        productos_destacados = [dict(r) for r in cur.fetchall()]

        # Últimos agregados
        cur.execute("""
            SELECT id,nombre,tipo,precio,stock
            FROM productos
            ORDER BY id DESC
            LIMIT 8
        """)
        productos_recientes = [dict(r) for r in cur.fetchall()]
    finally:
        conn.close()

    return render_page(
        "main/index.html",
        productos_destacados=productos_destacados,
        productos_recientes=productos_recientes,
        body_class="home"
    )

@main.route("/esencias")
def esencias():
    return render_page("main/esencias.html", body_class="esencias")

@main.route("/femeninos")
def femeninos():
    return render_page("main/femeninos.html", body_class="femenina")

@main.route("/masculinos")
def masculinos():
    return render_page("main/masculinos.html", body_class="masculina")

@main.route("/contacto")
def contacto():
    return render_page("main/contacto.html", body_class="contacto")

@main.route("/buscar")
def buscar():
    q = request.args.get("q", "").strip()
    resultados = []
    return render_page("main/buscar.html", q=q, resultados=resultados, body_class="buscar")

# Inicializa BD de productos al cargar módulo
init_db()

# ===================== CRUD PRODUCTOS =====================

# Listar + buscar
@main.route("/productos")
def productos_list():
    q = request.args.get("q", "").strip()
    conn = get_conn(); cur = conn.cursor()
    if q:
        cur.execute("""
            SELECT id,nombre,tipo,precio,stock
            FROM productos
            WHERE nombre LIKE ? OR tipo LIKE ?
            ORDER BY id DESC
        """, (f"%{q}%", f"%{q}%"))
    else:
        cur.execute("SELECT id,nombre,tipo,precio,stock FROM productos ORDER BY id DESC")
    productos = [dict(r) for r in cur.fetchall()]
    conn.close()
    return render_page("main/productos_list.html", productos=productos, q=q, body_class="productos")

# Crear
@main.route("/productos/nuevo", methods=["GET", "POST"])
def productos_create():
    if request.method == "POST":
        nombre = (request.form.get("nombre") or "").strip()
        tipo   = (request.form.get("tipo")   or "").strip()
        precio = float((request.form.get("precio") or "0").replace(",", "."))
        stock  = int(request.form.get("stock") or "0")

        if not nombre or not tipo:
            flash("Nombre y tipo son obligatorios.", "danger")
            return redirect(url_for("main.productos_create"))

        conn = get_conn(); cur = conn.cursor()
        cur.execute("""
            INSERT INTO productos(nombre,tipo,precio,stock)
            VALUES(?,?,?,?)
        """, (nombre, tipo, precio, stock))
        conn.commit(); conn.close()
        flash("Producto creado correctamente.", "success")
        return redirect(url_for("main.productos_list"))

    return render_page("main/productos_form.html", modo="crear", prod=None, body_class="productos")

# Editar
@main.route("/productos/<int:pid>/editar", methods=["GET", "POST"])
def productos_edit(pid):
    conn = get_conn(); cur = conn.cursor()
    if request.method == "POST":
        nombre = (request.form.get("nombre") or "").strip()
        tipo   = (request.form.get("tipo")   or "").strip()
        precio = float((request.form.get("precio") or "0").replace(",", "."))
        stock  = int(request.form.get("stock") or "0")

        cur.execute("""
            UPDATE productos
               SET nombre=?, tipo=?, precio=?, stock=?
             WHERE id=?
        """, (nombre, tipo, precio, stock, pid))
        conn.commit(); conn.close()
        flash("Producto actualizado.", "success")
        return redirect(url_for("main.productos_list"))

    cur.execute("SELECT id,nombre,tipo,precio,stock FROM productos WHERE id=?", (pid,))
    row = cur.fetchone(); conn.close()
    if not row:
        flash("Producto no encontrado.", "warning")
        return redirect(url_for("main.productos_list"))

    prod = dict(row)
    return render_page("main/productos_form.html", modo="editar", prod=prod, body_class="productos")

# Eliminar
@main.route("/productos/<int:pid>/eliminar", methods=["POST"])
def productos_delete(pid):
    conn = get_conn(); cur = conn.cursor()
    cur.execute("DELETE FROM productos WHERE id=?", (pid,))
    conn.commit(); conn.close()
    flash("Producto eliminado.", "info")
    return redirect(url_for("main.productos_list"))

# Diagnóstico: ver rutas registradas
@main.route("/_routes")
def _routes():
    from flask import current_app
    return "<pre>" + "\n".join(sorted(map(str, current_app.url_map.iter_rules()))) + "</pre>"
