from flask import Flask
from .extensions import db, migrate, jwt
# from .config import get_config
from .routes import all_routes
import os


def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///budgetwise.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    for r in all_routes:
        app.register_blueprint(r)


    db.init_app(app)
    migrate.init_app(app, db)

    return app