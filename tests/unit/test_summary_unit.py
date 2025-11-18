import pytest
from datetime import date as dt_date
from decimal import Decimal

from app.extensions import db
from app.models.category import Category
from app.models.transaction import Transaction
from app.services.summary_services import SummaryService
from app.utils.summary_exceptions import SummaryNotFoundError, InvalidPeriodTypeError


# --------------------------------------------------------
# HELPER: Seed category + transaction
# --------------------------------------------------------
def seed_transaction(
    user_id=1,
    amount=100,
    tx_type="expense",
    cat_name="Food",
    created=dt_date(2025, 1, 10),
    app=None,
):
    """Add category + transaction inside app context."""
    with app.app_context():
        category = Category.query.filter_by(name=cat_name, user_id=user_id).first()
        if not category:
            category = Category(name=cat_name, type=tx_type, user_id=user_id)
            db.session.add(category)
            db.session.commit()

        tr = Transaction(
            user_id=user_id,
            category_id=category.id,
            amount=Decimal(amount),
            description="test",
            type=tx_type,
            created_date=created,
            updated_at=created,
        )
        db.session.add(tr)
        db.session.commit()

        return category, tr


# --------------------------------------------------------
# PERIOD SUMMARY — SUCCESS
# --------------------------------------------------------
def test_summary_by_period_success(app):
    seed_transaction(app=app, amount=200, tx_type="income", cat_name="Salary")
    seed_transaction(app=app, amount=50, tx_type="expense", cat_name="Food")

    result = SummaryService.get_summary_by_period(
        user_id=1,
        period_type="year",
        tx_type=None,
        start="2025",
        end="2025",
    )

    # Convert Pydantic model to dict for easy access
    data = result.model_dump()

    assert data["transactions_count"] == 2
    assert data["income_transaction_total"] == 200.0
    assert data["expense_transaction_total"] == 50.0
    assert data["net_difference"] == 150.0


# --------------------------------------------------------
# PERIOD SUMMARY — NO DATA FOUND
# --------------------------------------------------------
def test_summary_by_period_no_data(app):
    with pytest.raises(SummaryNotFoundError):
        SummaryService.get_summary_by_period(
            user_id=1,
            period_type="year",
            start="2020",
            end="2020",
        )


# --------------------------------------------------------
# PERIOD SUMMARY — INVALID PERIOD TYPE
# --------------------------------------------------------
def test_summary_by_period_invalid_period(app):
    with pytest.raises(InvalidPeriodTypeError):
        SummaryService.get_summary_by_period(
            user_id=1,
            period_type="weird",
            start="2025",
            end="2025",
        )


# --------------------------------------------------------
# SUBCATEGORY SUMMARY — SUCCESS
# --------------------------------------------------------
def test_summary_by_subcategory_success(app):
    seed_transaction(app=app, tx_type="income", amount=500, cat_name="Bonus")
    seed_transaction(app=app, tx_type="income", amount=200, cat_name="Bonus")

    result = SummaryService.get_summary_by_subcategory(
        user_id=1,
        period_type="year",
        start="2025",
        end="2025",
        subcategory="Bonus",
    )

    data = result.model_dump()

    assert data["transactions_count"] == 2
    assert data["total_income"] == 700.0
    # Access breakdown properly using CategorySummary fields
    income_breakdown = data["summary_breakdown"]["income"][0]
    assert income_breakdown["category"] == "Bonus"
    assert income_breakdown["total"] == 700.0


# --------------------------------------------------------
# SUBCATEGORY — NO DATA FOUND
# --------------------------------------------------------
def test_summary_by_subcategory_no_data(app):
    with pytest.raises(SummaryNotFoundError):
        SummaryService.get_summary_by_subcategory(
            user_id=1,
            period_type="year",
            start="2020",
            end="2020",
            subcategory="Food",
        )
