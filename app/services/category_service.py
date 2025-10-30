from app.models.category import Category
from app.extensions import db

class CategoryService:
    @staticmethod
    def create_category(name, type, user_id):
        # Check if the same user already has a category with this name
        existing = Category.query.filter_by(name=name, user_id=user_id).first()
        if existing:
            raise ValueError("Category already exists for this user")

        category = Category(name=name, type=type, user_id=user_id)
        db.session.add(category)
        db.session.commit()
        return category

    @staticmethod
    def get_all_categories(user_id):
        return Category.query.filter_by(user_id=user_id).all()
    
    @staticmethod
    def get_category(category_id, user_id):
        return Category.query.filter_by(user_id=user_id,id=category_id).first()
    
    @staticmethod
    def delete_category(category_id, user_id):
        category = Category.query.filter_by(id=category_id, user_id=user_id).first()
        if not category:
            raise ValueError("Category not found or unauthorized access")
        db.session.delete(category)
        db.session.commit()
        return True

    @staticmethod
    def update_category(category_id, name, type, user_id):
        category = Category.query.filter_by(id=category_id, user_id=user_id).first()
        if not category:
            raise ValueError("Category not found or unauthorized access")

        # Update only if new values are provided
        if name is not None:
            category.name = name
        if type is not None:
            category.type = type  # only update if explicitly passed

        db.session.commit()
        return category

    
