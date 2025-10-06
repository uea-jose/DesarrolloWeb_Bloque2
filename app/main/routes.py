# app/main/routes.py
import sqlite3
from flask import render_template, request, redirect, url_for, flash, make_response, jsonify
from .db import get_conn, init_db, fetch_products_by_gender, apply_stock, nombre_existe, ensure_unique_index
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

# ================== CATÁLOGOS (con carrito) ==================
@main.route("/femeninos")
def femeninos():
    # Soporta: "Femenino", "F", "femenina", etc.
    rows = fetch_products_by_gender("Femenino")
    return render_page(
        "main/femeninos.html",   # template estilo "frutas" adaptado a femeninos
        gender="F",
        products=rows,
        body_class="femenina"
    )

@main.route("/masculinos")
def masculinos():
    rows = fetch_products_by_gender("Masculino")
    return render_page(
        "main/masculinos.html",
        gender="M",
        products=rows,
        body_class="masculina"
    )

@main.post("/api/stock/apply")
def api_stock_apply():
    """
    Body JSON: {"slug":"acqua-di-gio", "delta": +1 | -1}
      +1 = reservar (resta stock)
      -1 = devolver (suma stock)
    """
    data = request.get_json(force=True) or {}
    slug  = data.get("slug")
    delta = int(data.get("delta", 0))
    if not slug or delta == 0:
        return jsonify({"ok": False, "error": "payload_invalido"}), 400

    ok, new_stock = apply_stock(slug, delta)
    if not ok and delta > 0:
        # No alcanzó el stock para reservar
        return jsonify({"ok": False, "reason": "out_of_stock", "stock": new_stock}), 409

    return jsonify({"ok": True, "slug": slug, "stock": new_stock})



@main.get("/api/productos/check_nombre")
def api_check_nombre():
    nombre = (request.args.get("nombre") or "").strip()
    exclude_id = request.args.get("exclude_id")
    try:
        exclude_id = int(exclude_id) if exclude_id not in (None, "", "null") else None
    except Exception:
        exclude_id = None
    return jsonify({"available": not nombre_existe(nombre, exclude_id)})
# --------- Otras páginas ---------
@main.route("/contacto")
def contacto():
    return render_page("main/contacto.html", body_class="contacto")

@main.route("/buscar")
def buscar():
    q = request.args.get("q", "").strip()
    resultados = []
    return render_page("main/buscar.html", q=q, resultados=resultados, body_class="buscar")

# Inicializa BD de productos al cargar módulo (idempotente)
init_db()

# Garantiza índice único por nombre (idempotente)
try:
    ensure_unique_index()
except Exception:
    pass

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
        # Validar unicidad
        if nombre_existe(nombre):
            conn.close()
            flash("Ya existe un producto con ese nombre.", "warning")
            return redirect(url_for("main.productos_create"))
        try:
            cur.execute("""
                INSERT INTO productos(nombre,tipo,precio,stock)
                VALUES(?,?,?,?)
            """, (nombre, tipo, precio, stock))
            conn.commit(); conn.close()
        except sqlite3.IntegrityError:
            conn.rollback(); conn.close()
            flash("Nombre duplicado. Debe ser único.", "danger")
            return redirect(url_for("main.productos_create"))
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

        # Unicidad al editar
        if nombre_existe(nombre, exclude_id=pid):
            conn.close()
            flash("Ese nombre ya está en uso por otro producto.", "warning")
            return redirect(url_for("main.productos_edit", pid=pid))

        try:
            cur.execute("""
                UPDATE productos
                   SET nombre=?, tipo=?, precio=?, stock=?
                 WHERE id=?
            """, (nombre, tipo, precio, stock, pid))
            conn.commit(); conn.close()
            flash("Producto actualizado.", "success")
            return redirect(url_for("main.productos_list"))
        except sqlite3.IntegrityError:
            conn.rollback(); conn.close()
            flash("Nombre duplicado. Debe ser único.", "danger")
            return redirect(url_for("main.productos_edit", pid=pid))

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

# Diagnóstico: ver rutas registradas (útil)
@main.route("/_routes")
def _routes():
    from flask import current_app
    return "<pre>" + "\n".join(sorted(map(str, current_app.url_map.iter_rules()))) + "</pre>"
