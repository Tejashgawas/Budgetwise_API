from flask import Blueprint, request, jsonify
from pydantic import ValidationError
from app.utils.protected import auth_required
from app.schemas.category_schema import CategoryCreateSchema, CategoryResponseSchema, CategoryUpdateSchema
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
        user_id = request.user_id
        validated = CategoryCreateSchema(**data)

        category = CategoryService.create_category(
            name=validated.name, type=validated.type, user_id=user_id
        )

        return (
            jsonify({
                "message": "Category created successfully",
                "category": CategoryResponseSchema.model_validate(category).model_dump()
            }),
            201,
        )
    except ValidationError as e:
        return jsonify({"errors": e.errors()}), 400
   

# -----------------------------
# Get All Categories (User-Specific)
# -----------------------------
@category_bp.route("/", methods=["GET"])
@auth_required
def get_all_categories():
    
    user_id = request.user_id
    categories = CategoryService.get_all_categories(user_id)
    response = [CategoryResponseSchema.model_validate(c).model_dump() for c in categories]
    return jsonify(response), 200
    

# -----------------------------
# Get Category (id-Specific)
# -----------------------------
@category_bp.route("/<int:category_id>", methods=["GET"])
@auth_required
def get_category(category_id):
    
    user_id = request.user_id
    category = CategoryService.get_category(category_id,user_id)
        
    response = CategoryResponseSchema.model_validate(category).model_dump()
    return jsonify(response), 200
    

# -----------------------------
# Update Category
# -----------------------------
@category_bp.route("/<int:category_id>", methods=["PUT"])
@auth_required
def update_category(category_id):
    try:
        data = request.get_json()
        user_id = request.user_id
        validated = CategoryUpdateSchema(**data)

        updated = CategoryService.update_category(
            category_id=category_id,
            name=validated.name,
            type=validated.type,
            user_id=user_id
        )

        return (
            jsonify({
                "message": "Category updated successfully",
                "category": CategoryResponseSchema.model_validate(updated).model_dump()
            }),
            200,
        )
    except ValidationError as e:
        return jsonify({"errors": e.errors()}), 400
    

# -----------------------------
# Delete Category
# -----------------------------
@category_bp.route("/<int:category_id>", methods=["DELETE"])
@auth_required
def delete_category(category_id):
 
    user_id = request.user_id
    CategoryService.delete_category(category_id, user_id)
    return jsonify({"message": "Category deleted successfully"}), 200
  