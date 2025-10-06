import os, math
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required
from . import products_bp
from ..db import listar_productos_paginado, contar_productos, obtener_producto, listar_categorias, crear_producto, actualizar_producto, eliminar_producto

@products_bp.route('/')
@login_required
def home():
    return redirect(url_for('products.listar'))


@products_bp.route('/listar')
@login_required
def listar():
    page = request.args.get('page', 1, type=int)
    per_page = int(os.getenv('PRODUCTS_PER_PAGE', '10'))

    total = contar_productos()
    total_pages = max(1, math.ceil(total / per_page))
    # clamp
    page = 1 if page < 1 else (total_pages if page > total_pages else page)
    offset = (page - 1) * per_page

    productos = listar_productos_paginado(per_page, offset)

    # Ventana (p-2 .. p+2)
    window = 2
    start = max(1, page - window)
    end = min(total_pages, page + window)
    pages = list(range(start, end + 1)) or [1]

    return render_template('productos_list.html',
                           productos=productos,
                           page=page, total_pages=total_pages, pages=pages)
@products_bp.route('/nuevo', methods=['GET','POST'])
@login_required
def nuevo():
    categorias = listar_categorias()
    if request.method == 'POST':
        nombre = (request.form.get('nombre') or '').strip()
        descripcion = (request.form.get('descripcion') or '').strip()
        categoria_id = request.form.get('categoria_id') or None
        precio = request.form.get('precio') or 0
        stock = int(request.form.get('stock') or 0)
        if len(nombre) < 2:
            flash('El nombre debe tener al menos 2 caracteres.', 'danger')
            return render_template('producto_form.html', categorias=categorias, data=request.form, modo='nuevo')
        crear_producto(nombre, descripcion, int(categoria_id) if categoria_id else None, precio, stock)
        flash('Producto creado correctamente.', 'success')
        return redirect(url_for('products.listar'))
    return render_template('producto_form.html', categorias=categorias, modo='nuevo')

@products_bp.route('/<int:prod_id>/editar', methods=['GET','POST'])
@login_required
def editar(prod_id):
    categorias = listar_categorias()
    data = obtener_producto(prod_id)
    if not data:
        flash('Producto no encontrado.', 'warning')
        return redirect(url_for('products.listar'))
    if request.method == 'POST':
        nombre = (request.form.get('nombre') or '').strip()
        descripcion = (request.form.get('descripcion') or '').strip()
        categoria_id = request.form.get('categoria_id') or None
        precio = request.form.get('precio') or 0
        stock = int(request.form.get('stock') or 0)
        if len(nombre) < 2:
            flash('El nombre debe tener al menos 2 caracteres.', 'danger')
            return render_template('producto_form.html', categorias=categorias, data=request.form, modo='editar', prod_id=prod_id)
        actualizar_producto(prod_id, nombre, descripcion, int(categoria_id) if categoria_id else None, precio, stock)
        flash('Producto actualizado.', 'success')
        return redirect(url_for('products.listar'))
    return render_template('producto_form.html', categorias=categorias, data=data, modo='editar', prod_id=prod_id)

@products_bp.route('/<int:prod_id>/eliminar', methods=['POST'])
@login_required
def eliminar(prod_id):
    eliminar_producto(prod_id)
    flash('Producto eliminado.', 'info')
    return redirect(url_for('products.listar'))
