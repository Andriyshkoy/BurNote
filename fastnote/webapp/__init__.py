from flask import Blueprint

bp = Blueprint('webapp', __name__)

from . import errors, routes
