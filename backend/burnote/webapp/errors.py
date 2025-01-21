from flask import render_template

from . import bp
from burnote import db


@bp.errorhandler(404)
def page_not_found(error):
    return render_template('errors/404.html'), 404


@bp.errorhandler(500)
def internal_server_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500
