Mejora: Nombre de producto ÚNICO (case-insensitive)

¿Qué se agregó?
1) Índice único en BD sobre lower(nombre) (idempotente).
   - Función: ensure_unique_index() en app/main/db.py
   - Se invoca al importar rutas (después de init_db())

2) Verificación en servidor (Flask).
   - app/main/routes.py:
     * Endpoint GET /api/productos/check_nombre?nombre=...&exclude_id=ID
     * Validación en crear y editar:
       - Si el nombre existe: flash y no guarda
       - Manejo de sqlite3.IntegrityError por seguridad

3) Verificación en vivo en el formulario.
   - app/templates/main/productos_form.html:
     * Script que consulta el endpoint y muestra
       'Disponible' o 'Ya existe un producto con ese nombre'.

Cómo probar rápido (local):
  - pip install -r requirements.txt
  - python run.py
  - Abrir http://127.0.0.1:5000/productos
  - Crear un producto con un nombre A; intentar crear otro con el mismo nombre A
    -> Debería impedirlo con mensaje.
  - Editar un producto y cambiar su nombre a uno que ya exista
    -> También lo impide.
