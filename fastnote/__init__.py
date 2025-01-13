from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from settings import Config

db = SQLAlchemy()
migrate = Migrate()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.json.ensure_ascii = False

    db.init_app(app)
    migrate.init_app(app, db)

    from fastnote.webapp import bp as webapp_bp
    app.register_blueprint(webapp_bp)

    return app
