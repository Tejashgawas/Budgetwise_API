from flask import Blueprint, Response, request, jsonify
from app.services.transaction_service import (
    create_transaction,
    get_transactions,
    update_transaction,
    get_transaction_by_id,
    delete_transaction
)

from app.schemas.transaction_schemas import (
    TransactionCreateSchema,
    TransactionUpdateSchema,
    TransactionResponseSchema,
    TransactionFilterSchema
  
)

from app.utils.protected import auth_required
from pydantic import ValidationError

transaction_bp = Blueprint("transactions", __name__)


# --------------------------------------------
# CREATE Transaction
# --------------------------------------------
@transaction_bp.route("/log-transaction", methods=["POST"])
@auth_required
def create_transaction_route():
    try:
        payload = request.get_json() or {}
        data = TransactionCreateSchema(**payload)
        user_id = request.user_id
        transaction_resp = create_transaction(user_id,data)  # returns TransactionResponseSchema
        return Response(transaction_resp.model_dump_json(), mimetype="application/json", status=201)
    except ValidationError as ve:
        # Simplify Pydantic validation messages
        errors = [
            {
                "field": ".".join(map(str, err["loc"])),
                "message": err["msg"]
            }
            for err in ve.errors()
        ]
        return jsonify({"validation_errors": errors}), 422

    except Exception as e:
        return jsonify({"error": str(e)}), 400


# --------------------------------------------
# GET All Transactions (optional filters)
# --------------------------------------------
@transaction_bp.route("/", methods=["GET"])
@auth_required
def get_all_transactions_route():
    user_id = request.user_id
    try:
        # Parse and validate query params with Pydantic
        q = request.args.to_dict()
        filter_schema = TransactionFilterSchema(**q)
        filters = filter_schema.dict(exclude_none=True)

        transactions = get_transactions(user_id, filters)  # returns list[TransactionResponseSchema]
        
        return jsonify(transactions), 200
    
    except ValidationError as ve:
         # Simplify Pydantic validation messages
        errors = [
            {
                "field": ".".join(map(str, err["loc"])),
                "message": err["msg"]
            }
            for err in ve.errors()
        ]
        return jsonify({"validation_errors": errors}), 422

    except Exception as e:
        return jsonify({"error": str(e)}), 400



# --------------------------------------------
# GET Single Transaction by ID
# --------------------------------------------
@transaction_bp.route("/<int:transaction_id>", methods=["GET"])
@auth_required
def get_transaction_by_id_route(transaction_id):
    user_id = request.user_id
    transaction = get_transaction_by_id(transaction_id, user_id)  # TransactionResponseSchema | None
    if not transaction:
        return jsonify({"message": "Transaction not found"}), 404
    return Response(transaction.model_dump_json(), mimetype="application/json", status=200)

# --------------------------------------------
# UPDATE Transaction
# --------------------------------------------
@transaction_bp.route("/<int:transaction_id>", methods=["PUT"])
@auth_required
def update_transaction_route(transaction_id):
    try:
        payload = request.get_json() or {}
        data = TransactionUpdateSchema(**payload)
        user_id = request.user_id
        transaction = update_transaction(transaction_id, data, user_id)  # TransactionResponseSchema | None
        if not transaction:
            return jsonify({"message": "Transaction not found"}), 404
        return Response(transaction.model_dump_json(), mimetype="application/json", status=200)
    except ValidationError as ve:
         # Simplify Pydantic validation messages
        errors = [
            {
                "field": ".".join(map(str, err["loc"])),
                "message": err["msg"]
            }
            for err in ve.errors()
        ]
        return jsonify({"validation_errors": errors}), 422

    except Exception as e:
        return jsonify({"error": str(e)}), 400

# --------------------------------------------
# DELETE Transaction
# --------------------------------------------
@transaction_bp.route("/<int:transaction_id>", methods=["DELETE"])
@auth_required
def delete_transaction_route(transaction_id):
    user_id = request.user_id
    deleted = delete_transaction(transaction_id, user_id)
    if not deleted:
        return jsonify({"message": "Transaction not found"}), 404
    return jsonify({"message": "Transaction deleted successfully"}), 200