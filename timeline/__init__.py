from flask import Blueprint

timeline_bp = Blueprint('timeline', __name__, template_folder='../templates')

from . import routes  # Importa las rutas para que se registren
