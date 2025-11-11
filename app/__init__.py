from flask import Flask,request, jsonify, render_template
from .extensions import db, migrate
from .config import get_config
import os
from app.utils.auth_exceptions import *
from pydantic import ValidationError
from app.utils.transaction_exceptions import *

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

    # =========================
    # AUTH ERROR HANDLERS
    # =========================
    error_map = {
        UserAlreadyExistsError: (400, "User already exists."),
        InvalidCredentialsError: (401, "Invalid credentials."),
        UserNotFoundError: (404, "User not found."),
        TokenMissingError: (401, "Authorization header missing."),
        TokenInvalidFormatError: (401, "Invalid authorization header format."),
        TokenExpiredError: (401, "Token expired."),
        TokenInvalidError: (401, "Invalid token."),
        SecretKeyMissingError: (500, "Internal configuration missing."),
        CategoryNotFoundError: (404, "Category not found."),
        TransactionNotFoundError: (404, "Transaction not found."),
        TransactionDatabaseError: (500, "Transaction database error."),
    }


    for exc, (code, default_msg) in error_map.items():
        @app.errorhandler(exc)
        def handle_auth_error(error, code=code, default_msg=default_msg):
            msg = str(error) if str(error) else default_msg

         
            return jsonify({"message": msg}), code
            
    @app.errorhandler(ValidationError)
    def handle_pydantic_validation(error):
        return jsonify({
            "message": "Invalid input data",
            "errors": error.errors()
        }), 400

    return app
