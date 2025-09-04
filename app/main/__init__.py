# app/main/__init__.py
from flask import Blueprint
from .db import init_db

main_bp = Blueprint(
    "main", __name__,
    # ⬇️ Cambia esto: que apunte a /templates, no /templates/main
    template_folder="../../templates",
    static_folder="../../static"
)

# Alias opcional
main = main_bp

# Inicializa la BD
init_db()

# Importa rutas
from . import routes
from . import usuarios_routes
