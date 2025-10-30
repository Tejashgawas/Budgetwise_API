from app.extensions import db
from app.models.user import User
from app.utils.security import hash_password
from app import create_app  # assuming you have create_app() factory

def seed_users():
    """Seeds the database with 10 demo users."""
    app = create_app()  # Initialize your Flask app context
    with app.app_context():
        users_data = [
            {"username": "yadnesh", "email": "yadnesh@example.com"},
            {"username": "gaurang", "email": "gaurang@example.com"},
            {"username": "deepti", "email": "deepti@example.com"},
            {"username": "abimanyu", "email": "abimanyu@example.com"},
            {"username": "aman", "email": "aman@example.com"},
            {"username": "brian", "email": "brian@example.com"},
            {"username": "dhruv", "email": "dhruv@example.com"},
            {"username": "gauravi", "email": "gauravi@example.com"},
            {"username": "junaid", "email": "junaid@example.com"},
            {"username": "nashua", "email": "nashua@example.com"}
        ]

        # Optional: clear existing users (use carefully)
        # db.session.query(User).delete()

        for data in users_data:
            if not User.query.filter_by(email=data["email"]).first():
                user = User(
                    username=data["username"],
                    email=data["email"],
                    password_hash=hash_password("password123")  # same password for all
                )
                db.session.add(user)

        db.session.commit()
        print(f"✅ Seeded {len(users_data)} users successfully!")

if __name__ == "__main__":
    seed_users()
