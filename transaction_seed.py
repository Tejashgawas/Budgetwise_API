from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.transaction import Transaction
from app.models.category import Category
from app.schemas.transaction_schemas import TransactionCreateSchema
from app.services.transaction_service import create_transaction
from decimal import Decimal
from datetime import date, timedelta
import random
from app.utils.security import hash_password

def seed_users():
    users_data = [
        {"username": "yadnes3h", "email": "yadnesh1@example.com"},
        {"username": "gauran3g", "email": "gaurang3@example.com"},
        {"username": "deept3i", "email": "deepti3@example.com"},
        {"username": "abimany3u", "email": "abimanyu3@example.com"},
        {"username": "aman3", "email": "aman3@example.com"},
        {"username": "brian3", "email": "brian3@example.com"},
        {"username": "dhruv3", "email": "dhruv3@example.com"},
        {"username": "gaurav3i", "email": "gauravi3@example.com"},
        {"username": "junaid3", "email": "junaid3@example.com"},
        {"username": "nashua3", "email": "nashua3@example.com"},
    ]

    users = []
    for u in users_data:
        existing_user = User.query.filter_by(email=u["email"]).first()
        if not existing_user:
            hash = hash_password("password123")
            user = User(username=u["username"], email=u["email"], password_hash=hash)
            db.session.add(user)
            users.append(user)
    db.session.commit()
    return User.query.all()  # return all users for transactions


def seed_transactions():
    app = create_app()
    with app.app_context():
        users = seed_users()

        categories_income = ["Salary", "Freelancing", "Interest", "Bonus", "Investment"]
        categories_expense = ["Food", "Transport", "Shopping", "Bills", "Entertainment", "Health"]

        for user in users:
            print(f"Seeding transactions for {user.username}...")

            for i in range(15):
                tx_type = random.choice(["income", "expense"])
                category_name = (
                    random.choice(categories_income)
                    if tx_type == "income"
                    else random.choice(categories_expense)
                )

                amount = round(random.uniform(100, 5000), 2)
                description = f"{tx_type.capitalize()} for {category_name}"

                # Create transaction schema (Pydantic)
                tx_schema = TransactionCreateSchema(
                    amount=Decimal(str(amount)),
                    type=tx_type,
                    category_name=category_name,
                    description=description,
                    date=date.today() - timedelta(days=random.randint(0, 30))
                )

                # Call your existing service function
                create_transaction(user.id, tx_schema)

        print("✅ Seeding complete: Users + Transactions added.")


if __name__ == "__main__":
    seed_transactions()
