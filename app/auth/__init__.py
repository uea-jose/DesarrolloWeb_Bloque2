
from flask import Blueprint

# Blueprint para las rutas de autenticación
auth_bp = Blueprint('auth', __name__)

# Importa las rutas para que queden registradas en el blueprint
from . import routes  # noqa: E402,F401
