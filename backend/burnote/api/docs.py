from flask import render_template

from . import bp


@bp.route('/docs')
def redoc():
    return render_template('pages/redoc.html')
