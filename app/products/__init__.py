from flask import Blueprint
products_bp = Blueprint('products', __name__, url_prefix='/dashboard/productos', template_folder='../templates')
from . import routes  # noqa
