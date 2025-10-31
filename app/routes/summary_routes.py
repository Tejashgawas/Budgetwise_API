from flask import Blueprint, Response, jsonify, request
from app.models import Category, Transaction, User
from app.schemas.transaction_schemas import TransactionCreateSchema
from app.services.transaction_service import create_transaction
from app.utils.protected import auth_required
from app.extensions import db
from app.services.summary_services import (
    get_summary_by_period,
    get_summary_by_subcategory
)
from pydantic import ValidationError
from sqlalchemy import func




summary_bp = Blueprint('summary', __name__)

@summary_bp.route('/', methods=['GET'])
def test():
    return jsonify({"message": "Success"}), 200


@summary_bp.route('/add', methods=['POST'])
def add_transaction():
    try:
        payload = request.get_json() or {}
        data = TransactionCreateSchema(**payload)
        user_id = request.user_id
        transaction_resp = create_transaction(user_id, data)
        return jsonify(transaction_resp.dict()), 201
    except ValidationError as e:
        return jsonify({"errors": e.errors()}), 400


@summary_bp.route("/get", methods=["GET"])
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
    period_value = request.args.get("period_value")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    tx_type = request.args.get("type")

    result = get_summary_by_period(user_id, period_type, period_value, tx_type, start_date, end_date)
    return Response(result.model_dump_json(), mimetype="application/json")


@summary_bp.route("/subcategory", methods=["GET"])
@auth_required
def summary_by_subcategory():
    user_id = request.user_id
    period_type = request.args.get("period_type", "month")
    period_value = request.args.get("period_value")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    tx_type = request.args.get("type")
    subcategory = request.args.get("sub")

    result = get_summary_by_subcategory(user_id, period_type, period_value, tx_type, start_date, end_date, subcategory)
    return Response(result.model_dump_json(), mimetype="application/json")
