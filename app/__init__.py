from flask import Flask
from .extensions import db, migrate, jwt
from .config import get_config
import os



def create_app():
    app = Flask(__name__)

    # Load configuration
    env_name = os.getenv('FLASK_ENV', 'development')
    config_class = get_config(env_name)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Import models
    from app.models import user, category, transaction

    # ✅ Register blueprints
    from app.routes.category_routes import category_bp
    app.register_blueprint(category_bp)


    return app
