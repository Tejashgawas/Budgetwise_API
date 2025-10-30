from app.models.category import Category
from app.extensions import db

class CategoryService:
    @staticmethod
    def create_category(name, type):
        existing = Category.query.filter_by(name=name).first()
        if existing:
            raise ValueError("Category already exists")

        category = Category(name=name, type=type)
        db.session.add(category)
        db.session.commit()
        return category

    @staticmethod
    def get_all_categories():
        return Category.query.all()

    @staticmethod
    def delete_category(category_id):
        category = Category.query.get(category_id)
        if not category:
            raise ValueError("Category not found")
        db.session.delete(category)
        db.session.commit()
        return True
