from flask import Blueprint, request, jsonify
from app.services.category_service import create_category, get_all_categories, delete_category
category_bp = Blueprint("categories", __name__, url_prefix="/categories")

@category_bp.route("", methods=["POST"])
def add_category():
    data = request.get_json()
    name = data.get("name")
    type = data.get("type")  # Must be 'income' or 'expense'

    if not name or not type:
        return jsonify({"error": "Both 'name' and 'type' are required"}), 400

    if type not in ["income", "expense"]:
        return jsonify({"error": "Invalid type. Must be 'income' or 'expense'."}), 400

    category, error = create_category(name, type)
    if error:
        return jsonify({"error": error}), 400

    return jsonify({
        "id": category.id,
        "name": category.name,
        "type": category.type
    }), 201


@category_bp.route("", methods=["GET"])
def list_categories():
    categories = get_all_categories()
    return jsonify([
        {"id": cat.id, "name": cat.name, "type": cat.type}
        for cat in categories
    ]), 200


@category_bp.route("/<int:category_id>", methods=["DELETE"])
def remove_category(category_id):
    category, error = delete_category(category_id)
    if error:
        return jsonify({"error": error}), 404

    return jsonify({"message": "Category deleted successfully"}), 200
