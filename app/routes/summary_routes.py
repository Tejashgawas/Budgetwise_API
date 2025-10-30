from flask import Blueprint, jsonify, request
from app.models import Category, Transaction, User
from app.schemas.transaction_schemas import TransactionCreateSchema
from app.services.transaction_service import create_transaction
from app.utils.protected import auth_required
from app.extensions import db
from app.schemas.summary_schema import SummaryResponse
from app.services.summary_services import (
    get_summary_by_period,
    get_summary_by_subcategory
)
from app.schemas.summary_schema import SummaryResponse
from pydantic import ValidationError
from sqlalchemy import func
from datetime import datetime
from decimal import Decimal

summary_bp = Blueprint('summary', __name__)

@summary_bp.route('/', methods=['GET'])
def test():
    return jsonify({
        "message": "Success",
    }), 200

##Dummy endpoint to add data
@summary_bp.route('/add', methods=['POST'])
def add_transaction():
    try:
        payload = request.get_json() or {}
        data = TransactionCreateSchema(**payload)
        user_id = request.user_id
        transaction_resp = create_transaction(user_id,data)  # returns TransactionResponseSchema
        return jsonify(transaction_resp.dict()), 201
    except ValidationError as e:
        return jsonify({"errors": e.errors()}), 400


##Dummy endpoint to get data
@summary_bp.route("/get", methods=["GET"])
def get_all_transactions():

    # Join with Category to get category name & type
    query = Transaction.query.join(Category)

    results = [
        {
            "id": t.id,
            "amount": str(t.amount),
            "created_date": t.created_date.isoformat() if t.created_date else None,
            "updated_at": t.updated_at.isoformat() if t.updated_at else None,
            "category": t.category.name,
            "type": t.category.type,  # comes from Category model
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

# @summary_bp.route('/monthly', methods=['GET'])
# def monthly_summary():
#     # ✅ Get query parameter
#     month = request.args.get('month')  # e.g., "2025-10"

#     if not month:
#         return jsonify({"error": "Month parameter (YYYY-MM) is required"}), 400

#     try:
#         # Parse YYYY-MM into start and end dates
#         start_date = datetime.strptime(month, "%Y-%m")
#         # compute next month
#         if start_date.month == 12:
#             end_date = datetime(start_date.year + 1, 1, 1)
#         else:
#             end_date = datetime(start_date.year, start_date.month + 1, 1)
#     except ValueError:
#         return jsonify({"error": "Invalid month format. Use YYYY-MM"}), 400

#     # ✅ Base query for the given month
#     base_query = db.session.query(Transaction).filter(
#         Transaction.date >= start_date,
#         Transaction.date < end_date
#     )

#     # ✅ Totals
#     total_income = base_query.filter(Transaction.type == 'income') \
#                              .with_entities(db.func.sum(Transaction.amount)).scalar() or 0
#     total_expense = base_query.filter(Transaction.type == 'expense') \
#                               .with_entities(db.func.sum(Transaction.amount)).scalar() or 0
#     net_savings = total_income - total_expense

#     return jsonify({
#         "month": month,
#         "total_income": f"{total_income:.2f}",
#         "total_expense": f"{total_expense:.2f}",
#         "net_savings": f"{net_savings:.2f}"
#     }), 200

# @summary_bp.route('/category', methods=['GET'])
# def category_summary():
#     # ✅ Get optional query parameters
#     start_date = request.args.get('start_date')
#     end_date = request.args.get('end_date')

#     # ✅ Base query: join transactions and categories
#     query = db.session.query(
#         Category.name.label("category"),
#         db.func.sum(Transaction.amount).label("total_spending")
#     ).join(Category).filter(Transaction.type == 'expense')

#     # ✅ Apply date filters if provided
#     if start_date and end_date:
#         query = query.filter(Transaction.date.between(start_date, end_date))

#     # ✅ Group and order by category
#     query = query.group_by(Category.name).order_by(db.desc("total_spending"))

#     results = query.all()

#     # ✅ Format JSON response
#     data = [
#         {"category": row.category, "total_spending": float(row.total_spending or 0)}
#         for row in results
#     ]

#     return jsonify({
#         "start_date": start_date,
#         "end_date": end_date,
#         "data": data
#     }), 200

# @summary_bp.route('/daterange', methods=['GET'])
# def summary_daterange():

#     # ✅ Get query parameters
#     start_date = request.args.get('start_date')
#     end_date = request.args.get('end_date')

#     if not start_date or not end_date:
#         return jsonify({"error": "start_date and end_date are required"}), 400

#     # ✅ Base query for the given date range
#     base_query = db.session.query(Transaction).filter(
#         Transaction.date.between(start_date, end_date)
#     )

#     # ✅ Calculate totals
#     total_income = base_query.filter(Transaction.type == 'income') \
#                              .with_entities(db.func.sum(Transaction.amount)).scalar() or 0

#     total_expense = base_query.filter(Transaction.type == 'expense') \
#                               .with_entities(db.func.sum(Transaction.amount)).scalar() or 0

#     net_savings = total_income - total_expense

#     # ✅ Return formatted response
#     return jsonify({
#         "total_income": f"{total_income:.2f}",
#         "total_expense": f"{total_expense:.2f}",
#         "net_savings": f"{net_savings:.2f}"
#     }), 200

@summary_bp.route("/period", methods=["GET"])
# @auth_required
def summary_by_period():
    """
    Query params:
      period_type = month | year
      period_value = e.g., 2025-10 or 2025
      type = income | expense | all
      start_date = date
      end_date = date
    """
    # user_id = request.user_id
    user_id = 1
    period_type = request.args.get("period_type", "month")
    period_value = request.args.get("period_value")
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    tx_type = request.args.get("type")
    print(user_id, period_type, period_value, tx_type)

    result = get_summary_by_period(user_id, period_type, period_value, tx_type, start_date, end_date)
    return jsonify(result.model_dump())


# 3️⃣ Summary by Subcategory
@summary_bp.route("/subcategory", methods=["GET"])
# @auth_required
def summary_by_subcategory():
    """
    Query params:
      subcategory_name
      month / year / start_date / end_date
      type = income | expense
    """
    user_id = request.user_id
    filters = {
        "subcategory_id": request.args.get("subcategory_id"),
        "subcategory_name": request.args.get("subcategory_name"),
        "month": request.args.get("month"),
        "year": request.args.get("year"),
        "start_date": request.args.get("start_date"),
        "end_date": request.args.get("end_date"),
        "type": request.args.get("type"),
    }

    result = get_summary_by_subcategory(user_id, filters)
    return jsonify(SummaryResponse(**result).model_dump())