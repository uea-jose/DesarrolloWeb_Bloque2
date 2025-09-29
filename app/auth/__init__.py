from flask import Blueprint
auth_bp = Blueprint('auth', __name__, template_folder='../templates/auth')

# importa rutas para registrar endpoints
from . import routes  # noqa: F401
