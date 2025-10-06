# app/main/routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from .db import get_conn, init_db

main = Blueprint('main', __name__)

# --------- Páginas existentes ---------
@main.route('/')
def index():
    conn = get_conn(); cur = conn.cursor()
    try:
        cur.execute("SELECT * FROM productos ORDER BY stock DESC, id DESC LIMIT 4")
        productos_destacados = cur.fetchall()
    finally:
        conn.close()
    return render_template('main/index.html', productos_destacados=productos_destacados)
@main.route('/esencias')
def esencias():
    return render_template('main/esencias.html')

@main.route('/femeninos')
def femeninos():
    return render_template('main/femeninos.html')

@main.route('/masculinos')
def masculinos():
    return render_template('main/masculinos.html')

@main.route('/contacto')
def contacto():
    return render_template('main/contacto.html')

@main.route('/buscar')
def buscar():
    q = request.args.get('q', '').strip()
    resultados = []
    return render_template('main/buscar.html', q=q, resultados=resultados)

# ---------- Inicializa la BD al cargar el módulo ----------
init_db()

# ===================== CRUD PRODUCTOS =====================

# LISTAR + BUSCAR
@main.route("/productos")
def productos_list():
    q = request.args.get("q", "").strip()
    conn = get_conn(); cur = conn.cursor()
    if q:
        cur.execute("""SELECT * FROM productos
                       WHERE nombre LIKE ? OR tipo LIKE ?
                       ORDER BY id DESC""", (f"%{q}%", f"%{q}%"))
    else:
        cur.execute("SELECT * FROM productos ORDER BY id DESC")
    productos = cur.fetchall()
    conn.close()
    return render_template("main/productos_list.html", productos=productos, q=q)

# CREAR
@main.route("/productos/nuevo", methods=["GET", "POST"])
def productos_create():
    if request.method == "POST":
        nombre = request.form.get("nombre","").strip()
        tipo   = request.form.get("tipo","").strip()
        precio = float(request.form.get("precio","0").replace(",", "."))
        stock  = int(request.form.get("stock","0"))
        if not nombre or not tipo:
            flash("Nombre y tipo son obligatorios.", "danger")
            return redirect(url_for("main.productos_create"))
        conn = get_conn(); cur = conn.cursor()
        cur.execute("INSERT INTO productos(nombre,tipo,precio,stock) VALUES(?,?,?,?)",
                    (nombre, tipo, precio, stock))
        conn.commit(); conn.close()
        flash("Producto creado correctamente.", "success")
        return redirect(url_for("main.productos_list"))
    return render_template("main/productos_form.html", modo="crear", prod=None)

# EDITAR
@main.route("/productos/<int:pid>/editar", methods=["GET", "POST"])
def productos_edit(pid):
    conn = get_conn(); cur = conn.cursor()
    if request.method == "POST":
        nombre = request.form.get("nombre","").strip()
        tipo   = request.form.get("tipo","").strip()
        precio = float(request.form.get("precio","0").replace(",", "."))
        stock  = int(request.form.get("stock","0"))
        cur.execute("""UPDATE productos
                       SET nombre=?, tipo=?, precio=?, stock=?
                       WHERE id=?""", (nombre, tipo, precio, stock, pid))
        conn.commit(); conn.close()
        flash("Producto actualizado.", "success")
        return redirect(url_for("main.productos_list"))
    cur.execute("SELECT * FROM productos WHERE id=?", (pid,))
    prod = cur.fetchone(); conn.close()
    if not prod:
        flash("Producto no encontrado.", "warning")
        return redirect(url_for("main.productos_list"))
    return render_template("main/productos_form.html", modo="editar", prod=prod)

# ELIMINAR
@main.route("/productos/<int:pid>/eliminar", methods=["POST"])
def productos_delete(pid):
    conn = get_conn(); cur = conn.cursor()
    cur.execute("DELETE FROM productos WHERE id=?", (pid,))
    conn.commit(); conn.close()
    flash("Producto eliminado.", "info")
    return redirect(url_for("main.productos_list"))