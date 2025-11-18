from flask import Response
from app.extensions import db
from app.models.transaction import Transaction
from app.models.category import Category
from app.schemas.transaction_schemas import (
    TransactionCreateSchema,
    TransactionUpdateSchema,
    TransactionResponseSchema,
)
from datetime import datetime as dt_date
from datetime import datetime
from app.utils.protected import auth_required
import json

from app.utils.transaction_exceptions import (
    CategoryNotFoundError,
    TransactionNotFoundError,
    TransactionDatabaseError
)
from flask import current_app

# -----------------------------
# Create Transaction
# -----------------------------

def create_transaction(user_id: int, transaction_data: TransactionCreateSchema):
    try:
        category = None

        if transaction_data.category_id:
            category = Category.query.filter_by(id = transaction_data.category_id).first()
        elif transaction_data.category_name:
            category = Category.query.filter_by(
                name=transaction_data.category_name, type=transaction_data.type,user_id=user_id
            ).first()
            if not category:
                category = Category(
                    name=transaction_data.category_name, type=transaction_data.type,user_id=user_id
                )
                db.session.add(category)
                db.session.flush()
        
        if not category:
            raise CategoryNotFoundError("Category not found or provided.")
        
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
                        date=(
                transaction.created_date.strftime("%Y-%m-%d")
                if isinstance(transaction.created_date, (dt_date, datetime))
                else str(transaction.created_date)
                ),
            user_id=transaction.user_id,
        )
    except CategoryNotFoundError as cnfe:
        raise cnfe
    except Exception as e:
        db.session.rollback()
        raise TransactionDatabaseError(f"Database error: {str(e)}")

# -----------------------------
# Get All Transactions (with filters)
# -----------------------------
def get_transactions(user_id: int, filters: dict):

    try:
        query = Transaction.query.filter_by(user_id=user_id)

        if filters.get("type"):
            query = query.filter_by(type=filters["type"])
        if filters.get("category"):
            query = query.join(Category).filter(Category.name == filters["category"])
        if filters.get("start_date"):
            query = query.filter(Transaction.created_date >= filters["start_date"])
        if filters.get("end_date"):
            query = query.filter(Transaction.created_date <= filters["end_date"])

        page = int(filters.get("page", 1))
        per_page = int(filters.get("per_page", 10))
        pagination = query.order_by(Transaction.created_date.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        result_models = [
            TransactionResponseSchema(
                id=t.id,
                amount=round(float(t.amount), 2),
                type=t.type,
                category=t.category.name,
                description=t.description,
                date=(
                t.created_date.strftime("%Y-%m-%d")
                if isinstance(t.created_date, (dt_date, datetime))
                else str(t.created_date)
                ),
                user_id=t.user_id,
            )
            for t in pagination.items
        ]

        response = {
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total_pages": pagination.pages,
            "total_items": pagination.total,
            "transactions": [
                json.loads(m.model_dump_json()) for m in result_models
            ],
        }

        return response
    except Exception as e:
        raise TransactionDatabaseError(f"Database error: {str(e)}")
# -----------------------------
# Get Transaction by ID
# -----------------------------
def get_transaction_by_id(transaction_id: int, user_id: int):
    try:

        transaction = Transaction.query.filter_by(
            id=transaction_id, user_id=user_id
        ).first()
        if not transaction:
            return None

        return TransactionResponseSchema(
            id=transaction.id,
            amount=round(float(transaction.amount), 2),
            type=transaction.type,
            category=transaction.category.name,
            description=transaction.description,
                        date=(
                transaction.created_date.strftime("%Y-%m-%d")
                if isinstance(transaction.created_date, (dt_date, datetime))
                else str(transaction.created_date)
                ),
            user_id=transaction.user_id,
        )
    except TransactionNotFoundError:
        raise
    except Exception as e:
        current_app.logger.error(f"[TRANSACTION] Get by ID error: {str(e)}")
        raise TransactionDatabaseError("Failed to retrieve transaction.")


# -----------------------------
# Update Transaction
# -----------------------------
def update_transaction(transaction_id: int, data: TransactionUpdateSchema, user_id: int):
    
    try:

        transaction = Transaction.query.filter_by(
            id=transaction_id, user_id=user_id
        ).first()
        if not transaction:
            raise TransactionNotFoundError(f"Transaction with ID {transaction_id} not found for user {user_id}.")

        if data.amount is not None:
            transaction.amount = round(float(data.amount), 2)
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
            amount=round(float(transaction.amount), 2),
            type=transaction.type,
            category=transaction.category.name,
            description=transaction.description,
                        date=(
                transaction.created_date.strftime("%Y-%m-%d")
                if isinstance(transaction.created_date, (dt_date, datetime))
                else str(transaction.created_date)
                ),
            user_id=transaction.user_id,
        
        )
    except TransactionNotFoundError:
        raise
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[TRANSACTION] Update error: {str(e)}")
        raise TransactionDatabaseError("Failed to update transaction.")
    


# -----------------------------
# Delete Transaction
# -----------------------------
def delete_transaction(transaction_id: int, user_id: int):
    try:
        transaction = Transaction.query.filter_by(
            id=transaction_id, user_id=user_id
        ).first()
        if not transaction:
            raise TransactionNotFoundError(f"Transaction ID {transaction_id} not found.")

        db.session.delete(transaction)
        db.session.commit()
        return True
    except TransactionNotFoundError:
        raise
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[TRANSACTION] Delete error: {str(e)}")
        raise TransactionDatabaseError("Failed to delete transaction.")