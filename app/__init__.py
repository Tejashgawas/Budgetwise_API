from flask import Flask
from .extensions import db, migrate
from .config import get_config
import os



def create_app():
    app = Flask(__name__)


    # Load configuration
    env_name = os.getenv('FLASK_ENV', 'development')
    config_class = get_config(env_name)
    app.config.from_object(config_class)


    db.init_app(app)
    migrate.init_app(app, db)

    # Import models
    from app.models import user, category, transaction
    
    # Register all routes
    from app.routes import api_bp
    app.register_blueprint(api_bp, url_prefix="/api")

    from app.reports import reports_blueprint
    app.register_blueprint(reports_blueprint, url_prefix="/reports")



    return app
