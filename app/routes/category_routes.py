from flask import Blueprint, request, jsonify
from pydantic import ValidationError
from app.utils.protected import auth_required
from app.schemas.category_schema import CategoryCreateSchema, CategoryResponseSchema
from app.services.category_service import CategoryService

category_bp = Blueprint("categories", __name__)

# -----------------------------
# Create Category
# -----------------------------
@category_bp.route("/", methods=["POST"])
@auth_required
def create_category():
    try:
        data = request.get_json()
        validated = CategoryCreateSchema(**data)

        category = CategoryService.create_category(
            name=validated.name, type=validated.type
        )

        return (
            jsonify(
                {"message": "Category created successfully",
                 "category": CategoryResponseSchema.model_validate(category).model_dump()}
            ),
            201,
        )
    except ValidationError as e:
        return jsonify({"errors": e.errors()}), 400
    except ValueError as e:
        return jsonify({"message": str(e)}), 400
    except Exception as e:
        return jsonify({"message": f"Unexpected error: {str(e)}"}), 500


# -----------------------------
# Get All Categories
# -----------------------------
@category_bp.route("/", methods=["GET"])
@auth_required
def get_all_categories():
    try:
        categories = CategoryService.get_all_categories()
        response = [CategoryResponseSchema.model_validate(c).model_dump() for c in categories]
        return jsonify(response), 200
    except Exception as e:
        return jsonify({"message": f"Unexpected error: {str(e)}"}), 500


# -----------------------------
# Delete Category
# -----------------------------
@category_bp.route("/<int:category_id>", methods=["DELETE"])
@auth_required
def delete_category(category_id):
    try:
        CategoryService.delete_category(category_id)
        return jsonify({"message": "Category deleted successfully"}), 200
    except ValueError as e:
        return jsonify({"message": str(e)}), 404
    except Exception as e:
        return jsonify({"message": f"Unexpected error: {str(e)}"}), 500
