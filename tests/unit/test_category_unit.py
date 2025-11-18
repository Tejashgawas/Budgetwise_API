import pytest
from app.services.category_service import CategoryService
from app.models.category import Category
from app.extensions import db
from app.utils.category_exceptions import (
    CategoryAlreadyExistsError,
    CategoryNotFoundError,
    CategoryDatabaseError,
)

# ---------------------------
# CREATE CATEGORY
# ---------------------------
def test_create_category_success(app):
    with app.app_context():
        cat = CategoryService.create_category(name="Food", type="expense", user_id=1)
        assert cat.id is not None
        assert cat.name == "Food"
        assert cat.type == "expense"

def test_create_category_duplicate(app):
    with app.app_context():
        CategoryService.create_category(name="Salary", type="income", user_id=1)
        with pytest.raises(CategoryAlreadyExistsError):
            CategoryService.create_category(name="Salary", type="income", user_id=1)

# ---------------------------
# GET ALL CATEGORIES
# ---------------------------
def test_get_all_categories(app):
    with app.app_context():
        CategoryService.create_category(name="Food", type="expense", user_id=2)
        cats = CategoryService.get_all_categories(user_id=2)
        assert isinstance(cats, list)
        assert all(isinstance(c, Category) for c in cats)

# ---------------------------
# GET CATEGORY BY ID
# ---------------------------
def test_get_category_success(app):
    with app.app_context():
        cat = CategoryService.create_category(name="Travel", type="expense", user_id=3)
        fetched = CategoryService.get_category(cat.id, user_id=3)
        assert fetched.id == cat.id

def test_get_category_not_found(app):
    with app.app_context():
        with pytest.raises(CategoryNotFoundError):
            CategoryService.get_category(9999, user_id=1)

# ---------------------------
# UPDATE CATEGORY
# ---------------------------
def test_update_category_success(app):
    with app.app_context():
        cat = CategoryService.create_category(name="Books", type="expense", user_id=4)
        updated = CategoryService.update_category(cat.id, name="Books Updated", type="income", user_id=4)
        assert updated.name == "Books Updated"
        assert updated.type == "income"

def test_update_category_not_found(app):
    with app.app_context():
        with pytest.raises(CategoryNotFoundError):
            CategoryService.update_category(9999, name="X", type="income", user_id=1)

# ---------------------------
# DELETE CATEGORY
# ---------------------------
def test_delete_category_success(app):
    with app.app_context():
        cat = CategoryService.create_category(name="DeleteMe", type="expense", user_id=5)
        result = CategoryService.delete_category(cat.id, user_id=5)
        assert result is True

def test_delete_category_not_found(app):
    with app.app_context():
        with pytest.raises(CategoryNotFoundError):
            CategoryService.delete_category(9999, user_id=1)
