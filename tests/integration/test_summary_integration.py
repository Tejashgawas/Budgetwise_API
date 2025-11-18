from datetime import date as dt_date
from decimal import Decimal

from app.extensions import db
from app.models.category import Category
from app.models.transaction import Transaction

# --------------------------------------------------------
# HELPER: add transaction inside app context
# --------------------------------------------------------
def add_tx(user_id, amount, tx_type, cat_name, created, app):
    """Add a transaction and category inside app context."""
    with app.app_context():
        # Check if category exists
        category = Category.query.filter_by(name=cat_name, user_id=user_id).first()
        if not category:
            category = Category(name=cat_name, type=tx_type, user_id=user_id)
            db.session.add(category)
            db.session.commit()

        tr = Transaction(
            user_id=user_id,
            category_id=category.id,
            amount=Decimal(amount),
            type=tx_type,
            created_date=created,
            updated_at=created,
            description="test",
        )
        db.session.add(tr)
        db.session.commit()
        return tr


# --------------------------------------------------------
# PERIOD SUMMARY — SUCCESS
# --------------------------------------------------------
def test_summary_period_integration(client, auth_header, app):
    add_tx(1, 200, "income", "Salary", dt_date(2025, 1, 10), app)
    add_tx(1, 50, "expense", "Food", dt_date(2025, 1, 15), app)

    res = client.get(
        "/api/summary/period?period_type=year&start=2025&end=2025",
        headers=auth_header,
    )

    assert res.status_code == 200
    data = res.json

    assert data["income_transaction_total"] == 200.0
    assert data["expense_transaction_total"] == 50.0
    assert data["net_difference"] == 150.0


# --------------------------------------------------------
# PERIOD SUMMARY — NO DATA
# --------------------------------------------------------
def test_summary_period_no_data(client, auth_header):
    res = client.get(
        "/api/summary/period?period_type=year&start=2020&end=2020",
        headers=auth_header,
    )
    assert res.status_code == 400
    assert "No transactions" in res.json["error"]


# --------------------------------------------------------
# SUBCATEGORY SUMMARY — SUCCESS
# --------------------------------------------------------
def test_summary_subcategory_integration(client, auth_header, app):
    add_tx(1, 300, "income", "Bonus", dt_date(2025, 1, 5), app)
    add_tx(1, 200, "income", "Bonus", dt_date(2025, 1, 6), app)

    res = client.get(
        "/api/summary/subcategory?period_type=year&start=2025&end=2025&subcategory=Bonus",
        headers=auth_header,
    )

    assert res.status_code == 200
    data = res.json

    assert data["transactions_count"] == 2
    assert float(data["total_income"]) == 500.0
    assert data["summary_breakdown"]["income"][0]["category"] == "Bonus"


# --------------------------------------------------------
# SUBCATEGORY SUMMARY — NOT FOUND
# --------------------------------------------------------
def test_summary_subcategory_no_data(client, auth_header):
    res = client.get(
        "/api/summary/subcategory?period_type=year&start=2020&end=2020&subcategory=Food",
        headers=auth_header,
    )
    assert res.status_code == 400


# --------------------------------------------------------
# DASHBOARD — SUCCESS
# --------------------------------------------------------
def test_dashboard_summary_integration(client, auth_header, app):
    add_tx(1, 500, "income", "Salary", dt_date(2025, 1, 1), app)
    add_tx(1, 200, "expense", "Food", dt_date(2025, 1, 2), app)

    res = client.get("/api/summary/dashboard", headers=auth_header)
    assert res.status_code == 200

    data = res.json
    assert data["total_income"] == 500.0
    assert data["total_expense"] == 200.0
    assert data["net_difference"] == 300.0
