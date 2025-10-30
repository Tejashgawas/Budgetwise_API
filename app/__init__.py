from flask import Flask
from .extensions import db, migrate, jwt
# from .config import get_config
import os



def create_app():
    app = Flask(__name__)


    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///budgetwise.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#     # Load configuration
#     env_name = os.getenv('FLASK_ENV', 'development')
#     config_class = get_config(env_name)
#     app.config.from_object(config_class)
# >>>>>>> 720e9b73a3b50d3e9d755006110fb869c5ddee47

    db.init_app(app)
    migrate.init_app(app, db)

    # Import models
    from app.models import user, category, transaction
    
    # Register all routes
    from app.routes import api_bp
    app.register_blueprint(api_bp, url_prefix="/api")



    return app
