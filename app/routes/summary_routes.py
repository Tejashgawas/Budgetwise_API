from flask import Blueprint, jsonify, request
from app.models import Category, Transaction, User
from app.extensions import db
from sqlalchemy import func
from datetime import datetime
from decimal import Decimal

summary_bp = Blueprint('summary', __name__)

@summary_bp.route('/summary', methods=['GET'])
def get_summary():
    return jsonify({
        "message": "Success",
    }), 200


##Dummy endpoint to add data
@summary_bp.route('/summary/add', methods=['POST'])
def add_transaction():
    data = request.get_json()
    print(data)

    t_type = data.get("type")
    amount = data.get("amount")
    category_name = data.get("category")
    description = data.get("description", "")
    t_date_str = data.get("date")  # comes as string, e.g. "2025-10-29"

    # Validation
    if not all([t_type, amount, category_name, t_date_str]):
        return jsonify({"error": "Missing required fields"}), 400

    # Convert string date → Python date object
    try:
        t_date = datetime.strptime(t_date_str, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

    # Check category
    category = Category.query.filter_by(name=category_name).first()
    if not category:
        category = Category(name=category_name, type=t_type)
        db.session.add(category)
        db.session.commit()

    # Create transaction
    transaction = Transaction(
        user_id=1,  # example user ID
        category_id=category.id,
        amount=Decimal(amount),
        description=description,
        created_date=t_date,
    )

    db.session.add(transaction)
    db.session.commit()

    return jsonify({
        "message": "Transaction added successfully",
        "id": transaction.id
    }), 201

##Dummy endpoint to get data
@summary_bp.route("/summary/get", methods=["GET"])
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
            "description": t.description
        }
        for t in query.all()
    ]

    return jsonify({
        "count": len(results),
        "transactions": results
    }), 200