from flask import Blueprint
admin_bp = Blueprint('admin', __name__, template_folder='../templates/admin', url_prefix='/admin')

# importa rutas para registrar endpoints
from . import routes  # noqa: F401
