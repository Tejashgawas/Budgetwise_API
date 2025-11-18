from app.models.category import Category
from app.models.transaction import Transaction
from app.extensions import db
from datetime import datetime

def to_date(s: str):
    return datetime.strptime(s, "%Y-%m-%d").date()

# HELPER: create category for tests
def seed_category(user_id=1, name="Food", type="expense"):
    cat = Category(name=name, type=type, user_id=user_id)
    db.session.add(cat)
    db.session.commit()
    return cat


# -----------------------------------------
# CREATE TRANSACTION
# -----------------------------------------
def test_create_transaction(client, auth_header):
    category = seed_category()   # Food / expense

    res = client.post(
        "/api/transactions/log-transaction",
        json={
            "amount": "250.00",
            "type": "expense",
            "category_id": category.id,
            "description": "Lunch",
            "date": "2025-11-10"
        },
        headers=auth_header
    )

    assert res.status_code == 201
    data = res.json
    assert float(data["amount"]) == 250.00
    assert data["category"] == "Food"
    assert data["description"] == "Lunch"
    assert data["type"] == "expense"


# -----------------------------------------
# GET ALL TRANSACTIONS
# -----------------------------------------
def test_get_transactions(client, auth_header):
    category = seed_category(name="Groceries")

    # Create a transaction
    client.post(
        "/api/transactions/log-transaction",
        json={
            "amount": "400",
            "type": "expense",
            "category_id": category.id,
            "description": "Veggies",
            "date": "2025-11-11"
        },
        headers=auth_header
    )

    res = client.get("/api/transactions/", headers=auth_header)
    assert res.status_code == 200
    data = res.json

    assert data["total_items"] == 1
    assert len(data["transactions"]) == 1
    assert data["transactions"][0]["category"] == "Groceries"


# -----------------------------------------
# GET TRANSACTION BY ID
# -----------------------------------------
def test_get_transaction_by_id(client, auth_header):
    category = seed_category(name="Bills")

    # Insert manually
    tr = Transaction(
        user_id=1,
        category_id=category.id,
        amount=300,
        description="Electricity",
        created_date=to_date("2025-10-02"),
        updated_at=to_date("2025-10-02"),
        type="expense"
    )
    db.session.add(tr)
    db.session.commit()

    res = client.get(f"/api/transactions/{tr.id}", headers=auth_header)
    
    assert res.status_code == 200
    assert res.json["id"] == tr.id
    assert res.json["category"] == "Bills"


# -----------------------------------------
# UPDATE TRANSACTION
# -----------------------------------------
def test_update_transaction(client, auth_header):
    category = seed_category(name="Fuel")

    # Create initial transaction
    res = client.post(
        "/api/transactions/log-transaction",
        json={
            "amount": "100",
            "type": "expense",
            "category_id": category.id,
            "description": "Petrol"
        },
        headers=auth_header
    )
    tr_id = res.json["id"]

    # Update it
    res2 = client.put(
        f"/api/transactions/{tr_id}",
        json={"amount": "150", "description": "Fuel refill"},
        headers=auth_header
    )

    assert res2.status_code == 200
    assert float(res2.json["amount"]) == 150.0
    assert res2.json["description"] == "Fuel refill"


# -----------------------------------------
# DELETE TRANSACTION
# -----------------------------------------
def test_delete_transaction(client, auth_header):
    category = seed_category(name="Travel")

    tr = Transaction(
        user_id=1,
        category_id=category.id,
        amount=500,
        description="Taxi",
        created_date=to_date("2025-10-02"),        # <-- FIXED
        updated_at=to_date("2025-10-02"), 
        type="expense"
    )
    db.session.add(tr)
    db.session.commit()

    res = client.delete(f"/api/transactions/{tr.id}", headers=auth_header)
    assert res.status_code == 200
    assert res.json["message"] == "Transaction deleted successfully"

    # Verify deletion
    assert Transaction.query.get(tr.id) is None