from flask import Blueprint, jsonify
from app.routes.auth_routes import auth_bp
from app.routes.transaction_routes import transaction_bp
from app.routes.category_routes import category_bp
from app.routes.summary_routes import summary_bp
from app.routes.csv_routes import csv_bp

# Master blueprint (optional grouping)
api_bp = Blueprint("api", __name__)

# # 🧩 Health check / root route
# @api_bp.route("/", methods=["GET"])
# def index():
#     return jsonify({"message": "BudgetWise API running successfully 🚀"}), 200

# Register sub-blueprints with prefixes
api_bp.register_blueprint(auth_bp, url_prefix="/auth")
api_bp.register_blueprint(transaction_bp, url_prefix="/transactions")
api_bp.register_blueprint(category_bp, url_prefix="/categories")
api_bp.register_blueprint(summary_bp, url_prefix="/summary")
api_bp.register_blueprint(csv_bp, url_prefix="/csv")
