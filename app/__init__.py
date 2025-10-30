from flask import Flask
from .extensions import db, migrate, jwt
# from .config import get_config
import os


def create_app():
    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///budgetwise.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate.init_app(app, db)

    # Register blueprints or routes here if needed
    from app.models import user, category, transaction
    
    # Register all routes
    from app.routes import api_bp
    app.register_blueprint(api_bp, url_prefix="/api")

    return app