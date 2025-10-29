from app.models.category import Category
from app.extensions import db

def create_category(name, type):
    # Check if category already exists
    existing = Category.query.filter_by(name=name).first()
    if existing:
        return None, "Category already exists."

    # Create new category
    category = Category(name=name, type=type)
    db.session.add(category)
    db.session.commit()
    return category, None


def get_all_categories():
    return Category.query.all()


def delete_category(category_id):
    category = Category.query.get(category_id)
    if not category:
        return None, "Category not found."

    db.session.delete(category)
    db.session.commit()
    return category, None
