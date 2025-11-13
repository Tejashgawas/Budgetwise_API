from app.models.category import Category
from app.extensions import db
from app.utils.category_exceptions import (
    CategoryAlreadyExistsError,
    CategoryNotFoundError,
    CategoryDatabaseError
)
from flask import current_app

class CategoryService:
    @staticmethod
    def create_category(name, type, user_id):
        # Check if the same user already has a category with this name
        try:
            existing = Category.query.filter_by(name=name, user_id=user_id).first()
            if existing:
                raise CategoryAlreadyExistsError("Category already exists for this user")

            category = Category(name=name, type=type, user_id=user_id)
            db.session.add(category)
            db.session.commit()
            return category
        except CategoryAlreadyExistsError:
            raise
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"[CATEGORY] Create error: {e}")
            raise CategoryDatabaseError("Failed to create category.")


    @staticmethod
    def get_all_categories(user_id):
        try:
            return Category.query.filter_by(user_id=user_id).all()

        except Exception as e:
            current_app.logger.error(f"[CATEGORY] Fetch all error: {e}")
            raise CategoryDatabaseError("Failed to fetch categories.")

    @staticmethod
    def get_category(category_id, user_id):
        try:
            category = Category.query.filter_by(user_id=user_id,id=category_id).first()
            if not category:
                raise CategoryNotFoundError("Category not found or unauthorized access.")
            return category
        except CategoryNotFoundError:
            raise
        except Exception as e:
            current_app.logger.error(f"[CATEGORY] Fetch error: {e}")
            raise CategoryDatabaseError("Failed to fetch category.")



    @staticmethod
    def delete_category(category_id, user_id):
        try:
            category = Category.query.filter_by(id=category_id, user_id=user_id).first()
            if not category:
                raise CategoryNotFoundError("Category not found or unauthorized access")
            db.session.delete(category)
            db.session.commit()
            return True
        except CategoryNotFoundError:
            raise
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"[CATEGORY] Delete error: {e}")
            raise CategoryDatabaseError("Failed to delete category.")

    @staticmethod
    def update_category(category_id, name, type, user_id):
        try:
            category = Category.query.filter_by(id=category_id, user_id=user_id).first()
            if not category:
                raise CategoryNotFoundError("Category not found or unauthorized access")

            # Update only if new values are provided
            if name is not None:
                category.name = name
            if type is not None:
                category.type = type  # only update if explicitly passed

            db.session.commit()
            return category
        except CategoryNotFoundError:
            raise
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"[CATEGORY] Update error: {e}")
            raise CategoryDatabaseError("Failed to update category.")

    
