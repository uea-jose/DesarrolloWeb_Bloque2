V6+/
├─ run.py                              # Punto de entrada: crea la app Flask y levanta el servidor
├─ requirements.txt                    # Dependencias de Python para reproducir el entorno
├─ readme.txt                          # Notas/instrucciones del proyecto (puedes ampliar aquí)
├─ .gitignore                          # Archivos y carpetas a excluir del control de versiones
├─ venv/                               # Entorno virtual (no se versiona)
├─ scripts/                            # Utilidades/automatizaciones (vacío u opcional)
├─ datos/
│  ├─ datos.csv                        # Datos de ejemplo/semillas (CSV)
│  ├─ datos.json                       # Datos de ejemplo/semillas (JSON)
│  └─ datos.txt                        # Datos de ejemplo/semillas (TXT)
├─ app/
│  ├─ __init__.py                      # Fábrica de app; registra blueprints, config básica
│  ├─ data/                            # Recursos de datos (por ej. DB SQLite física, si aplica)
│  ├─ main/                            # Lógica de negocio y rutas web
│  │  ├─ __init__.py                   # Define el Blueprint 'main'
│  │  ├─ db.py                         # Capa de datos (SQLite): conexión, init DB, queries, stock
│  │  ├─ routes.py                     # Rutas principales (home, catálogos, CRUD productos, API stock)
│  │  ├─ usuarios_routes.py            # Rutas para formularios/listas de usuarios (si están activas)
│  │  └─ routes_copy.py                # Copia de seguridad de rutas (referencia)
│  ├─ static/                          # Archivos estáticos (JS, CSS, imágenes)
│  │  ├─ Images_/                      # Recursos gráficos (carrusel, banners, etc.)
│  │  ├─ script.js                     # JS global del sitio (helpers, offcanvas, etc.)
│  │  ├─ script_femeninos.js           # Carrito Femeninos: agrega/quita, sincroniza stock (API)
│  │  ├─ script_masculinos.js          # Carrito Masculinos: igual a Femeninos pero para 'Masculino'
│  │  └─ styles.css                    # Estilos personalizados (layout, paleta, callout “Comprar”)
│  └─ templates/                       # Plantillas Jinja2 (HTML)
│     ├─ base.html                     # Layout global: navbar, footer y offcanvas Admin (#adminMenu)
│     └─ main/
│        ├─ index.html                 # Inicio: hero, carrusel, destacados, botón “Panel rápido”
│        ├─ index_copy.html            # Copia de respaldo del inicio (opcional)
│        ├─ femeninos.html             # Catálogo femenino + carrito (estructura base compartida)
│        ├─ masculinos.html            # Catálogo masculino + carrito (misma estructura, tema azul)
│        ├─ productos_list.html        # Listado/búsqueda de productos (CRUD)
│        ├─ productos_form.html        # Form crear/editar producto (CRUD)
│        ├─ buscar.html                # Página de resultados de búsqueda
│        ├─ esencias.html              # Página informativa/sección adicional
│        ├─ contacto.html              # Página de contacto
│        ├─ registrarse.html           # Página de registro de usuarios (UI)
│        ├─ usuarios_list.html         # Lista de usuarios (UI)
│        ├─ usuarios_form.html         # Form de usuario (UI)
│        └─ _productos_table.html      # Parcial reutilizable: tabla de productos (incluye badges/acciones)
