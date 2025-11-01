from flask import Blueprint, Response, jsonify, request
from app.models import Category, Transaction, User
from app.schemas.transaction_schemas import TransactionCreateSchema
from app.services.csv_services import import_transactions_via_route
from app.services.transaction_service import create_transaction
from app.utils.protected import auth_required
from app.extensions import db
from pydantic import ValidationError
from sqlalchemy import func

csv_bp = Blueprint('csv', __name__)

@csv_bp.route("/import", methods=["POST"])
@auth_required
def import_data():
    """
    Upload a CSV file and import transactions by calling the /log-transaction API for each row.
    """
    if "file" not in request.files:
        return jsonify({"error": "CSV file is required"}), 400

    file = request.files["file"]
    user_id = request.user_id

    try:
        # Save uploaded CSV temporarily
        temp_path = f"transactions.csv"
        file.save(temp_path)

        # Call your import logic
        response = import_transactions_via_route(temp_path,user_id)

        return jsonify(response), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500