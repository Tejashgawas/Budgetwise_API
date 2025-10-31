from app.models.transaction import Transaction
from app.models.category import Category
from app.extensions import db
from sqlalchemy import func, extract
from app.schemas.transaction_schemas import TransactionFilterSchema
from app.schemas.summary_schema import CategorySummary, SummaryResponse, SummaryResponseSubCategory
from datetime import date, datetime
from typing import Dict, List, Optional
import calendar

def get_summary_by_period(
    user_id: int,
    period_type: Optional[str] = None,
    period_value: Optional[str] = None,
    tx_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    if not period_type:
        period_type = "month"
    if not period_value:
        period_value = datetime.now().strftime("%Y-%m")

    query = (
        db.session.query(
            Category.name.label("category_name"),
            Category.type.label("category_type"),
            func.sum(Transaction.amount).label("total")
        )
        .join(Category)
        .filter(Transaction.user_id == user_id)
    )

    range_start, range_end = None, None

    if start_date and end_date:
        try:
            range_start = datetime.strptime(start_date, "%Y-%m-%d").date()
            range_end = datetime.strptime(end_date, "%Y-%m-%d").date()
            query = query.filter(
                Transaction.created_date.between(range_start, range_end)
            )
        except ValueError:
            raise ValueError("Invalid date format. Use YYYY-MM-DD for start_date and end_date.")
    else:
        if period_type == "month":
            year, month = map(int, period_value.split("-"))
            query = query.filter(
                extract("year", Transaction.created_date) == year,
                extract("month", Transaction.created_date) == month
            )
            range_start = date(year, month, 1)
            range_end = date(year, month, calendar.monthrange(year, month)[1])

        elif period_type == "year":
            year = int(period_value)
            query = query.filter(extract("year", Transaction.created_date) == year)
            range_start = date(year, 1, 1)
            range_end = date(year, 12, 31)

    if tx_type in ("income", "expense"):
        query = query.filter(Transaction.type == tx_type)

    results = query.group_by(Category.id, Category.name, Category.type).all()

    summary: Dict[str, list[CategorySummary]] = {"income": [], "expense": []}
    total_income = 0.0
    total_expense = 0.0

    for r in results:
        cat_summary = CategorySummary(category=r.category_name, total=float(r.total))
        if r.category_type == "income":
            summary["income"].append(cat_summary)
            total_income += float(r.total)
        elif r.category_type == "expense":
            summary["expense"].append(cat_summary)
            total_expense += float(r.total)

    response_data = {
        "type": tx_type or "all",
        "period": period_value,
        "start_date": range_start,
        "end_date": range_end,
        "transactions_count": len(results),
        "total_income": total_income,
        "total_expense": total_expense,
    }

    summary_response = SummaryResponse(**response_data)
    return summary_response


def get_summary_by_subcategory(
    user_id: int,
    period_type: Optional[str] = None,
    period_value: Optional[str] = None,
    tx_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    category_name: Optional[str] = None
):
    if not period_type:
        period_type = "month"
    if not period_value:
        period_value = datetime.now().strftime("%Y-%m")

    query = (
        db.session.query(
            Category.name.label("category_name"),
            Category.type.label("category_type"),
            func.sum(Transaction.amount).label("total")
        )
        .join(Category)
        .filter(Transaction.user_id == user_id)
    )

    range_start, range_end = None, None

    if start_date and end_date:
        try:
            range_start = datetime.strptime(start_date, "%Y-%m-%d").date()
            range_end = datetime.strptime(end_date, "%Y-%m-%d").date()
            query = query.filter(
                Transaction.created_date.between(range_start, range_end)
            )
        except ValueError:
            raise ValueError("Invalid date format. Use YYYY-MM-DD for start_date and end_date.")
    else:
        if period_type == "month":
            year, month = map(int, period_value.split("-"))
            query = query.filter(
                extract("year", Transaction.created_date) == year,
                extract("month", Transaction.created_date) == month
            )
            range_start = date(year, month, 1)
            range_end = date(year, month, calendar.monthrange(year, month)[1])

        elif period_type == "year":
            year = int(period_value)
            query = query.filter(extract("year", Transaction.created_date) == year)
            range_start = date(year, 1, 1)
            range_end = date(year, 12, 31)

    if tx_type in ("income", "expense"):
        query = query.filter(Transaction.type == tx_type)

    results = query.group_by(Category.id, Category.name, Category.type).all()

    if category_name:
        results = [r for r in results if r.category_name.lower() == category_name.lower()]

    summary: Dict[str, list[CategorySummary]] = {"income": [], "expense": []}
    total_income = 0.0
    total_expense = 0.0

    for r in results:
        cat_summary = CategorySummary(category=r.category_name, total=float(r.total))
        if r.category_type == "income":
            summary["income"].append(cat_summary)
            total_income += float(r.total)
        elif r.category_type == "expense":
            summary["expense"].append(cat_summary)
            total_expense += float(r.total)

    response_data = {
        "type": tx_type or "all",
        "period": period_value,
        "start_date": range_start,
        "end_date": range_end,
        "transactions_count": len(results),
        "total_income": total_income,
        "total_expense": total_expense,
        "summary": summary,
    }

    summary_response = SummaryResponseSubCategory(**response_data)
    return summary_response
