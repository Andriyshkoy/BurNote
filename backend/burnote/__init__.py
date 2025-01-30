from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy

from settings import Config

db = SQLAlchemy()
migrate = Migrate()
moment = Moment()
cors = CORS()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.json.ensure_ascii = False

    db.init_app(app)
    migrate.init_app(app, db)
    moment.init_app(app)
    cors.init_app(app,
                  resources={r'/api/*': {'origins': '*'}},
                  supports_credentials=True)

    from burnote.webapp import bp as webapp_bp
    app.register_blueprint(webapp_bp)

    from burnote.api import bp as api_bp
    app.register_blueprint(api_bp)

    return app
