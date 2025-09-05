# Mejora: Nombre de producto único (case-insensitive)

Asegura que cada perfume tenga **nombre único** (sin distinguir mayúsculas/minúsculas).
Incluye migración SQLite, validaciones en backend y verificación en vivo en el formulario.

## 1) Migración (SQLite)
```sql
CREATE UNIQUE INDEX IF NOT EXISTS idx_productos_nombre_ci ON productos(lower(nombre));
```
Si ya hay duplicados, límpialos primero:
```sql
SELECT lower(nombre) AS n, COUNT(*) c
FROM productos
GROUP BY lower(nombre)
HAVING c>1;
```

## 2) app/main/db.py
Añade:
```python
def ensure_unique_index():
    conn = get_conn(); cur = conn.cursor()
    cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_productos_nombre_ci ON productos(lower(nombre))")
    conn.commit(); conn.close()

def nombre_existe(nombre: str, exclude_id: int | None = None) -> bool:
    conn = get_conn(); cur = conn.cursor()
    if exclude_id is None:
        cur.execute("SELECT 1 FROM productos WHERE lower(nombre)=lower(?) LIMIT 1", (nombre,))
    else:
        cur.execute("SELECT 1 FROM productos WHERE lower(nombre)=lower(?) AND id<>? LIMIT 1", (nombre, exclude_id))
    ok = cur.fetchone() is not None
    conn.close()
    return ok
```
Y en `init_db()` agrega `ensure_unique_index()` al final.

## 3) app/main/routes.py
Importa:
```python
import sqlite3
from .db import nombre_existe
```

En **crear** (antes de insertar):
```python
if nombre_existe(nombre):
    flash("Ya existe un producto con ese nombre.", "warning")
    return redirect(url_for("main.productos_create"))
```
Protege el INSERT:
```python
try:
    # INSERT...
    conn.commit()
except sqlite3.IntegrityError:
    conn.rollback()
    flash("Nombre duplicado. Debe ser único.", "danger")
    return redirect(url_for("main.productos_create"))
```

En **editar**:
```python
if nombre_existe(nombre, exclude_id=pid):
    flash("Ese nombre ya está en uso por otro producto.", "warning")
    return redirect(url_for("main.productos_edit", pid=pid))
```
Protege el UPDATE con el mismo `try/except`.

**Endpoint opcional** (validación en vivo):
```python
@main.get("/api/productos/check_nombre")
def api_check_nombre():
    nombre = (request.args.get("nombre") or "").strip()
    exclude_id = request.args.get("exclude_id")
    exclude_id = int(exclude_id) if (exclude_id and exclude_id.isdigit()) else None
    return jsonify({"available": not nombre_existe(nombre, exclude_id)})
```

## 4) app/templates/main/productos_form.html (opcional UX)
Bajo el input nombre:
```html
<small id="estadoNombre" class="form-text"></small>
```
Script:
```html
{% block extra_js %}
<script>
const input = document.querySelector('input[name="nombre"]');
const estado = document.getElementById('estadoNombre');
const pid = {{ (prod.id if prod else 'null')|safe }};
if (input && estado) {
  let t; const set=(m,c)=>{estado.textContent=m; estado.className='form-text '+c;}
  input.addEventListener('input',()=>{
    clearTimeout(t);
    const nombre=input.value.trim();
    if(!nombre){ set('', ''); return; }
    t=setTimeout(async()=>{
      try{
        const url=new URL('{{ url_for("main.api_check_nombre") }}', window.location.origin);
        url.searchParams.set('nombre', nombre);
        if(pid) url.searchParams.set('exclude_id', pid);
        const r=await fetch(url); const data=await r.json();
        set(data.available ? 'Disponible ✓':'Ya existe un producto con ese nombre',
            data.available ? 'text-success':'text-danger');
      }catch(e){}
    },250);
  });
}
</script>
{% endblock %}
```
