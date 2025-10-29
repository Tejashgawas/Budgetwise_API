from flask import Blueprint
from app.routes.auth_routes import auth_bp
from app.routes.transaction_routes import transaction_bp


# Master blueprint (optional grouping)
api_bp = Blueprint("api", __name__)

# Register sub-blueprints with prefixes
api_bp.register_blueprint(auth_bp, url_prefix="/auth")
api_bp.register_blueprint(transaction_bp, url_prefix="/transactions")