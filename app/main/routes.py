# app/main/routes.py
from flask import render_template, request, redirect, url_for, flash, make_response, send_file, jsonify, session
from io import BytesIO
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas

from .db import (
    init_db, list_categorias, upsert_producto, get_producto,
    delete_producto, search_productos, nombre_existe, mysql_schema_sql
)
from . import main_bp as main
from app.security import login_required, role_required

def render_page(template_path: str, **context):
    resp = make_response(render_template(template_path, **context))
    resp.headers["Cache-Control"] = "no-store"
    return resp

@main.before_app_request
def _ensure_db():
    init_db()


@main.route("/")
def index():
    if not session.get("user_id"):
        return redirect(url_for("auth.login"))
    return redirect(url_for("admin.dashboard"))

@main.route("/productos")
def productos_list():
    q = request.args.get("q", "").strip() or None
    page = int(request.args.get("page", 1) or 1)
    per_page = int(request.args.get("per_page", 10) or 10)
    rows, total = search_productos(q=q, page=page, per_page=per_page)
    pages = (total + per_page - 1) // per_page
    return render_page("main/productos_list.html",
                       productos=rows, q=q, page=page, pages=pages, per_page=per_page, total=total)

@main.route("/productos/nuevo", methods=["GET", "POST"])
@role_required('admin')
def productos_create():
    categorias = list_categorias()
    if request.method == "POST":
        nombre = request.form.get("nombre","").strip()
        descripcion = request.form.get("descripcion","").strip() or None
        categoria_id = int(request.form.get("categoria_id"))
        precio = float(request.form.get("precio", "0") or 0)
        stock = int(request.form.get("stock", "0") or 0)
        if not nombre:
            flash("El nombre es obligatorio", "danger")
            return render_page("main/productos_form.html", categorias=categorias, prod=None)
        if nombre_existe(nombre):
            flash("Ya existe un producto con ese nombre", "danger")
            return render_page("main/productos_form.html", categorias=categorias, prod=None)
        new_id = upsert_producto(None, nombre, descripcion, categoria_id, precio, stock)
        flash("Producto creado.", "success")
        return redirect(url_for("main.productos_list"))
    return render_page("main/productos_form.html", categorias=categorias, prod=None)

@main.route("/productos/<int:pid>/editar", methods=["GET", "POST"])
@role_required('admin')
def productos_edit(pid):
    categorias = list_categorias()
    prod = get_producto(pid)
    if not prod:
        flash("No existe el producto", "warning")
        return redirect(url_for("main.productos_list"))
    if request.method == "POST":
        nombre = request.form.get("nombre","").strip()
        descripcion = request.form.get("descripcion","").strip() or None
        categoria_id = int(request.form.get("categoria_id"))
        precio = float(request.form.get("precio", "0") or 0)
        stock = int(request.form.get("stock", "0") or 0)
        if not nombre:
            flash("El nombre es obligatorio", "danger")
            return render_page("main/productos_form.html", categorias=categorias, prod=prod)
        if nombre_existe(nombre, exclude_id=pid):
            flash("Ya existe un producto con ese nombre", "danger")
            return render_page("main/productos_form.html", categorias=categorias, prod=prod)
        upsert_producto(pid, nombre, descripcion, categoria_id, precio, stock)
        flash("Producto actualizado.", "success")
        return redirect(url_for("main.productos_list"))
    return render_page("main/productos_form.html", categorias=categorias, prod=prod)

@main.route("/productos/<int:pid>/eliminar", methods=["POST"])
@role_required('admin')
def productos_delete(pid):
    delete_producto(pid)
    flash("Producto eliminado.", "info")
    return redirect(url_for("main.productos_list"))

@main.route("/productos/export/pdf")
def productos_export_pdf():
    q = request.args.get("q", "").strip() or None
    rows, total = search_productos(q=q, page=1, per_page=10000)
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=landscape(letter))
    textobject = c.beginText(40, 520)
    textobject.setFont("Helvetica-Bold", 14)
    textobject.textLine("Inventario de Productos")
    textobject.setFont("Helvetica", 10)
    headers = ["Código", "Nombre", "Descripción", "Categoría", "Stock", "Precio"]
    c.drawString(40, 500, " | ".join(headers))
    y = 480
    for r in rows:
        line = f"{r['id']:04d} | {r['nombre']} | {r['descripcion'] or ''} | {r['categoria']} | {r['stock']} | S/ {r['precio']:.2f}"
        c.drawString(40, y, line[:200])
        y -= 16
        if y < 40:
            c.showPage()
            y = 520
    c.showPage()
    c.save()
    buffer.seek(0)
    return send_file(buffer, mimetype="application/pdf", as_attachment=True, download_name="inventario.pdf")

@main.route("/_check_nombre")
def _check_nombre():
    nombre = request.args.get("nombre","").strip()
    exclude_id = request.args.get("exclude_id")
    exclude_id = int(exclude_id) if exclude_id and exclude_id.isdigit() else None
    available = not nombre_existe(nombre, exclude_id=exclude_id)
    return jsonify({"available": available})

@main.route("/_schema_mysql.sql")
def schema_mysql_download():
    sql = mysql_schema_sql()
    return make_response(sql, 200, {"Content-Type": "text/plain; charset=utf-8"})

# ---- Rutas de navegación del navbar (compatibilidad con plantillas) ----
@main.route("/esencias")
def esencias():
    # mostrar todo de categoría 'Esencia'
    q = "Esencia"
    page = int(request.args.get("page", 1) or 1)
    per_page = int(request.args.get("per_page", 10) or 10)
    rows, total = search_productos(q=q, page=page, per_page=per_page)
    pages = (total + per_page - 1) // per_page
    return render_page("main/productos_list.html",
                       productos=rows, q=q, page=page, pages=pages, per_page=per_page, total=total)

@main.route("/femeninos")
def femeninos():
    q = "Femenino"
    page = int(request.args.get("page", 1) or 1)
    per_page = int(request.args.get("per_page", 10) or 10)
    rows, total = search_productos(q=q, page=page, per_page=per_page)
    pages = (total + per_page - 1) // per_page
    return render_page("main/productos_list.html",
                       productos=rows, q=q, page=page, pages=pages, per_page=per_page, total=total)

@main.route("/masculinos")
def masculinos():
    q = "Masculino"
    page = int(request.args.get("page", 1) or 1)
    per_page = int(request.args.get("per_page", 10) or 10)
    rows, total = search_productos(q=q, page=page, per_page=per_page)
    pages = (total + per_page - 1) // per_page
    return render_page("main/productos_list.html",
                       productos=rows, q=q, page=page, pages=pages, per_page=per_page, total=total)

@main.route("/contacto")
def contacto():
    return render_page("main/contacto.html")
