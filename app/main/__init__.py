# package marker
# app/main/__init__.py
from flask import Blueprint
from .db import init_db

main_bp = Blueprint("main", __name__, template_folder="../../templates/main", static_folder="../../static")

# Inicializa la BD al importar el blueprint (primer arranque del servidor)
init_db()

from . import routes  # noqa
