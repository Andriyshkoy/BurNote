from flask import Blueprint
from flask_restful import Api

bp = Blueprint('api', __name__, url_prefix='/api')
api = Api(bp)

from . import resources
