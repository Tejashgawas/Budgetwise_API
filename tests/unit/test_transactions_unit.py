import pytest
from unittest.mock import patch, MagicMock
from decimal import Decimal
from datetime import date as dt_date

from app.services.transaction_service import (
    create_transaction,
    get_transaction_by_id,
    update_transaction,
    delete_transaction
)
from app.schemas.transaction_schemas import (
    TransactionCreateSchema,
    TransactionUpdateSchema
)
from app.utils.transaction_exceptions import (
    CategoryNotFoundError,
    TransactionNotFoundError
)
@patch("app.services.transaction_service.db")
@patch("app.services.transaction_service.Category")
@patch("app.services.transaction_service.Transaction")
def test_create_transaction_success(mock_transaction, mock_category, mock_db):
    # Mock category lookup
    mock_cat_instance = MagicMock()
    mock_cat_instance.id = 1
    mock_cat_instance.name = "Food"  # must be a string
    mock_category.query.filter_by.return_value.first.return_value = mock_cat_instance

    # Mock transaction instance with proper category relationship
    mock_tr = MagicMock()
    mock_tr.id = 10
    mock_tr.amount = Decimal("120.50")
    mock_tr.description = "Burger"
    mock_tr.type = "expense"
    mock_tr.user_id = 1
    mock_tr.created_date = dt_date(2025, 11, 10)
    mock_tr.category = mock_cat_instance  # link category object
    mock_transaction.return_value = mock_tr

    schema = TransactionCreateSchema(
        amount=Decimal("120.50"),
        type="expense",
        category_id=1,
        description="Burger",
        date=dt_date(2025, 11, 10)
    )

    resp = create_transaction(1, schema)

    assert resp.amount == Decimal("120.50")
    assert resp.category == "Food"
    mock_db.session.add.assert_called_once()


# ---------------------------------------
# CREATE TRANSACTION — CATEGORY NOT FOUND
# ---------------------------------------
@patch("app.services.transaction_service.Category")
def test_create_transaction_category_not_found(mock_category):
    mock_category.query.filter_by.return_value.first.return_value = None

    schema = TransactionCreateSchema(
        amount=Decimal("100.00"),
        type="expense",
        category_id=99,
        description="Test Expense",
        date=dt_date(2025, 11, 10),
    )

    with pytest.raises(CategoryNotFoundError):
        create_transaction(1, schema)


# ---------------------------------------
# GET TRANSACTION BY ID SUCCESS
# ---------------------------------------
@patch("app.services.transaction_service.Transaction")
@patch("app.services.transaction_service.Category")
def test_get_transaction_by_id_success(mock_category, mock_transaction,app):
    with app.app_context():
        mock_category = MagicMock()
        mock_category.name = "Bills"

        tr = MagicMock(
            id=5,
            amount=Decimal("400.00"),
            description="Electricity",
            type="expense",
            category=mock_category,  # use real string through MagicMock attribute
            user_id=1,
            created_date=dt_date(2025, 10, 2)
        )
        mock_transaction.query.filter_by.return_value.first.return_value = tr

        resp = get_transaction_by_id(5, 1)

        assert resp.id == 5
        assert resp.category == "Bills"
        assert resp.amount == Decimal("400.00")


# ---------------------------------------
# GET TRANSACTION BY ID — NOT FOUND
# ---------------------------------------
@patch("app.services.transaction_service.Transaction")
def test_get_transaction_by_id_not_found(mock_transaction):
    mock_transaction.query.filter_by.return_value.first.return_value = None

    resp = get_transaction_by_id(999, 1)
    assert resp is None


# ---------------------------------------
# UPDATE TRANSACTION SUCCESS
# ---------------------------------------
@patch("app.services.transaction_service.db")
@patch("app.services.transaction_service.Transaction")
def test_update_transaction_success(mock_transaction, mock_db, app):
    with app.app_context():  # ✅ ensures DB session works
        mock_category = MagicMock()
        mock_category.name = "Fuel"

        tr = MagicMock(
            id=3,
            amount=Decimal("100.00"),
            description="Old Description",
            type="expense",
            category=mock_category,
            user_id=1,
            created_date=dt_date(2025, 10, 5)
        )
        mock_transaction.query.filter_by.return_value.first.return_value = tr

        schema = TransactionUpdateSchema(
            amount=Decimal("150.00"),
            description="Updated Description"
        )

        resp = update_transaction(3, schema, 1)

        assert resp.amount == Decimal("150.00")
        assert resp.description == "Updated Description"
        mock_db.session.commit.assert_called_once()


# ---------------------------------------
# UPDATE TRANSACTION — NOT FOUND
# ---------------------------------------
@patch("app.services.transaction_service.Transaction")
def test_update_transaction_not_found(mock_transaction):
    mock_transaction.query.filter_by.return_value.first.return_value = None

    schema = TransactionUpdateSchema(amount=Decimal("200.00"))

    with pytest.raises(TransactionNotFoundError):
        update_transaction(200, schema, 1)


# ---------------------------------------
# DELETE TRANSACTION SUCCESS
# ---------------------------------------
@patch("app.services.transaction_service.db")
@patch("app.services.transaction_service.Transaction")
def test_delete_transaction_success(mock_transaction, mock_db):
    tr = MagicMock(id=7)
    mock_transaction.query.filter_by.return_value.first.return_value = tr

    resp = delete_transaction(7, 1)

    assert resp is True
    mock_db.session.delete.assert_called_once()
    mock_db.session.commit.assert_called_once()


# ---------------------------------------
# DELETE TRANSACTION — NOT FOUND
# ---------------------------------------
@patch("app.services.transaction_service.Transaction")
def test_delete_transaction_not_found(mock_transaction):
    mock_transaction.query.filter_by.return_value.first.return_value = None

    with pytest.raises(TransactionNotFoundError):
        delete_transaction(999, 1)
