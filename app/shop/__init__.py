from flask import Blueprint
shop_bp = Blueprint('shop', __name__, url_prefix='/dashboard/tienda', template_folder='../templates')
from . import routes  # noqa
