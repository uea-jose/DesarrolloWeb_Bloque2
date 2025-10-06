from flask import render_template, request, redirect, url_for, flash, session
from flask_login import login_required
from . import shop_bp
from ..db import (
    listar_productos_categoria_paginado, contar_productos_categoria,
    obtener_productos_por_ids, listar_categorias
)
import os, math

def _cart_get():
    return session.setdefault('cart', {})

def _cart_add(prod_id:int, qty:int=1):
    cart = _cart_get()
    prod_id = str(prod_id)
    cart[prod_id] = cart.get(prod_id, 0) + qty
    session['cart'] = cart
    session.modified = True

def _read_cart_items():
    cart = _cart_get()
    ids = [int(k) for k in cart.keys()]
    items = []
    total = 0.0
    if ids:
        prods = obtener_productos_por_ids(ids)
        for p in prods:
            qty = int(cart.get(str(p['id']), 0))
            sub = float(p['precio']) * qty
            total += sub
            items.append({'id': p['id'], 'nombre': p['nombre'], 'precio': float(p['precio']), 'qty': qty, 'subtotal': sub})
    return items, total

@shop_bp.route('/')
@login_required
def home():
    cats = listar_categorias()
    items, total = _read_cart_items()
    return render_template('store_home.html', categorias=cats, cart_items=items, cart_total=total)

@shop_bp.route('/<string:slug>')
@login_required
def categoria(slug:str):
    slug = slug.lower()
    page = request.args.get('page', 1, type=int)
    per_page = int(os.getenv('STORE_PER_PAGE', '9'))

    total = contar_productos_categoria(slug)
    total_pages = max(1, math.ceil(total / per_page))
    page = 1 if page < 1 else (total_pages if page > total_pages else page)
    offset = (page - 1) * per_page

    productos = listar_productos_categoria_paginado(slug, per_page, offset)

    window = 2
    start = max(1, page - window)
    end = min(total_pages, page + window)
    pages = list(range(start, end+1)) or [1]

    items, total_cart = _read_cart_items()

    return render_template('store_grid.html',
                           slug=slug, productos=productos,
                           page=page, total_pages=total_pages, pages=pages,
                           cart_items=items, cart_total=total_cart)

@shop_bp.route('/cart/add', methods=['POST'])
@login_required
def cart_add():
    pid = request.form.get('pid', type=int)
    qty = request.form.get('qty', type=int) or 1
    if not pid:
        flash('Producto inválido.', 'warning')
        return redirect(url_for('shop.home'))
    _cart_add(pid, qty)
    flash('Producto añadido al carrito.', 'success')
    ref = request.form.get('ref') or url_for('shop.home')
    return redirect(ref)
