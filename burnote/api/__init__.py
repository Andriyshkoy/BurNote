from flask import Blueprint

bp = Blueprint('api', __name__, url_prefix='/api')

from .v1 import bp as v1_bp
bp.register_blueprint(v1_bp)
