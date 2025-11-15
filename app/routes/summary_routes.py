from datetime import datetime
from flask import Blueprint, Response, jsonify, request
from app.models import Category, Transaction, User
from app.schemas.transaction_schemas import TransactionCreateSchema
from app.services.transaction_service import create_transaction
from app.utils.protected import auth_required
from app.extensions import db
from app.services.summary_services import SummaryService
from pydantic import ValidationError
from sqlalchemy import func
from app.utils.protected import auth_required
from app.utils.summary_exceptions import SummaryError

summary_bp = Blueprint('summary', __name__)

@summary_bp.route('/', methods=['GET'])
@auth_required
def test():
    return jsonify({"message": "Success"}), 200


# @summary_bp.route('/add', methods=['POST'])
# @auth_required
# def add_transaction():
#     try:
#         payload = request.get_json() or {}
#         data = TransactionCreateSchema(**payload)
#         user_id = request.user_id
#         transaction_resp = create_transaction(user_id, data)
#         return jsonify(transaction_resp.dict()), 201
#     except ValidationError as e:
#         return jsonify({"errors": e.errors()}), 400


@summary_bp.route("/get", methods=["GET"])
@auth_required
def get_all_transactions():
    query = Transaction.query.join(Category)
    results = [
        {
            "id": t.id,
            "amount": str(t.amount),
            "created_date": t.created_date.isoformat() if t.created_date else None,
            "updated_at": t.updated_at.isoformat() if t.updated_at else None,
            "category": t.category.name,
            "type": t.category.type,
            "description": t.description,
            "user_id": t.user_id,
            "category_id": t.category_id
        }
        for t in query.all()
    ]

    return jsonify({
        "count": len(results),
        "transactions": results
    }), 200


@summary_bp.route("/period", methods=["GET"])
@auth_required
def summary_by_period():
    user_id = request.user_id
    period_type = request.args.get("period_type", "month")
    tx_type = request.args.get("type")
    start = request.args.get("start")
    end = request.args.get("end")
    caller = request.args.get("caller")

    current_year = datetime.now().year
    if not start or not end:
        start = f"{current_year}-01-01"
        end = f"{current_year}-12-31"

    try:
        result = SummaryService.get_summary_by_period(user_id, period_type, tx_type, start, end, caller)
        # ✅ Flask can directly jsonify dicts
        return jsonify(result.model_dump()), 200
    except SummaryError as e:
        return jsonify({"error": str(e)}), 400


@summary_bp.route("/subcategory", methods=["GET"])
@auth_required
def summary_by_subcategory():
    user_id = request.user_id
    period_type = request.args.get("period_type", "month")
    tx_type = request.args.get("type")
    start = request.args.get("start")
    end = request.args.get("end")
    subcategory = request.args.get("subcategory")
    caller = request.args.get("caller")

    current_year = datetime.now().year
    if not start or not end:
        start = f"{current_year}-01-01"
        end = f"{current_year}-12-31"

    try:
        result = SummaryService.get_summary_by_subcategory(user_id, period_type, tx_type, start, end, subcategory ,caller)
        # ✅ Flask can directly jsonify dicts
        return jsonify(result.model_dump()), 200
    except SummaryError as e:
        return jsonify({"error": str(e)}), 400