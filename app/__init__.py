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
<<<<<<< HEAD
=======
    jwt.init_app(app)

    # Register blueprints or routes here if needed
    from app.models import user, category, transaction
    
    # Register all routes
    from app.routes import api_bp
    app.register_blueprint(api_bp, url_prefix="/api")
    
>>>>>>> 7cb7866a30afc765c01bbcff8cb1ddaf1465b8eb

    return app