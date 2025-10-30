from app.extensions import db
from app.models.transaction import Transaction
from app.models.category import Category
from app.schemas.transaction_schemas import (
    TransactionCreateSchema,
    TransactionUpdateSchema,
    TransactionResponseSchema,
    TransactionFilterSchema,
)
from datetime import datetime
from app.utils.protected import auth_required
# -----------------------------
# Create Transaction
# -----------------------------

def create_transaction(user_id: int, transaction_data: TransactionCreateSchema):

    category = None

    if transaction_data.category_id:
        category = Category.query.filter_by(id = transaction_data.category_id).first()
    elif transaction_data.category_name:
        category = Category.query.filter_by(
            name=transaction_data.category_name, type=transaction_data.type
        ).first()
        if not category:
            category = Category(
                name=transaction_data.category_name, type=transaction_data.type,user_id=user_id
            )
            db.session.add(category)
            db.session.commit()
            db.session.flush()
    
    if not category:
        raise ValueError("Category not found or provided.")
    
    transaction = Transaction(
        user_id=user_id,
        category_id=category.id,
        amount=transaction_data.amount,
        description=transaction_data.description,
        created_date=transaction_data.date or datetime.utcnow().date(),
        updated_at=datetime.utcnow(),
        type=transaction_data.type,  # new field added earlier
    )

    db.session.add(transaction)
    db.session.commit()

    return TransactionResponseSchema(
        id=transaction.id,
        amount=transaction.amount,
        type=transaction.type,
        category=category.name,
        description=transaction.description,
        date=transaction.created_date,
        user_id=transaction.user_id,
    )

# -----------------------------
# Get All Transactions (with filters)
# -----------------------------
def get_transactions(user_id: int, filters: dict):
    query = Transaction.query.filter_by(user_id=user_id)

    if filters.get("type"):
        query = query.filter_by(type=filters["type"])
    if filters.get("category"):
        query = query.join(Category).filter(Category.name == filters["category"])
    if filters.get("start_date"):
        query = query.filter(Transaction.created_date >= filters["start_date"])
    if filters.get("end_date"):
        query = query.filter(Transaction.created_date <= filters["end_date"])

    transactions = query.order_by(Transaction.created_date.desc()).all()

    return [
        TransactionResponseSchema(
            id=t.id,
            amount=t.amount,
            type=t.type,
            category=t.category.name,
            description=t.description,
            date=t.created_date,
            user_id=t.user_id,
        )
        for t in transactions
    ]

# -----------------------------
# Get Transaction by ID
# -----------------------------
def get_transaction_by_id(transaction_id: int, user_id: int):
    transaction = Transaction.query.filter_by(
        id=transaction_id, user_id=user_id
    ).first()
    if not transaction:
        return None

    return TransactionResponseSchema(
        id=transaction.id,
        amount=transaction.amount,
        type=transaction.type,
        category=transaction.category.name,
        description=transaction.description,
        date=transaction.created_date,
        user_id=transaction.user_id,
    )


# -----------------------------
# Update Transaction
# -----------------------------
def update_transaction(transaction_id: int, data: TransactionUpdateSchema, user_id: int):
    transaction = Transaction.query.filter_by(
        id=transaction_id, user_id=user_id
    ).first()
    if not transaction:
        return None

    if data.amount is not None:
        transaction.amount = data.amount
    if data.description is not None:
        transaction.description = data.description
    if data.category_id is not None:
        transaction.category_id = data.category_id
    if data.date is not None:
        transaction.created_date = data.date

    transaction.updated_at = datetime.utcnow()
    db.session.commit()

    return TransactionResponseSchema(
        id=transaction.id,
        amount=transaction.amount,
        type=transaction.type,
        category=transaction.category.name,
        description=transaction.description,
        date=transaction.created_date,
        user_id=transaction.user_id,
    
    )


# -----------------------------
# Delete Transaction
# -----------------------------
def delete_transaction(transaction_id: int, user_id: int):
    transaction = Transaction.query.filter_by(
        id=transaction_id, user_id=user_id
    ).first()
    if not transaction:
        return False

    db.session.delete(transaction)
    db.session.commit()
    return True