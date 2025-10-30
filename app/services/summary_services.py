from app.models.transaction import Transaction
from app.models.category import Category
from app.extensions import db
from sqlalchemy import func, extract
from app.schemas.transaction_schemas import TransactionFilterSchema
from app.schemas.summary_schema import CategorySummary, SummaryResponse
from datetime import date
from typing import Dict, List, Optional
from datetime import datetime

# ---------------- Summary by Period ----------------
from datetime import datetime, date
import calendar
from sqlalchemy import func, extract
from app.models import Transaction, Category
from app.extensions import db
from app.schemas.summary_schema import SummaryResponse, CategorySummary


def get_summary_by_period(
    user_id: int,
    period_type: Optional[str] = None,
    period_value: Optional[str] = None,
    tx_type: Optional[str] = None
):
    # 🧠 Default period handling
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

    # 🗓️ Filter by period (month or year)
    start_date, end_date = None, None

    if period_type == "month":
        year, month = map(int, period_value.split("-"))
        query = query.filter(
            extract("year", Transaction.created_date) == year,
            extract("month", Transaction.created_date) == month
        )
        start_date = date(year, month, 1)
        end_date = date(year, month, calendar.monthrange(year, month)[1])

    elif period_type == "year":
        year = int(period_value)
        query = query.filter(extract("year", Transaction.created_date) == year)
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)

    # 💰 Filter by transaction type if provided
    if tx_type in ("income", "expense"):
        query = query.filter(Transaction.type == tx_type)

    results = query.group_by(Category.id, Category.name, Category.type).all()

    # 📊 Build category summaries and totals
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

    # 🧾 Construct response data dictionary
    response_data = {
        "type": tx_type or "all",
        "period_type": period_type,
        "period": period_value,
        "start_date": start_date,
        "end_date": end_date,
        "summary": summary,
        "total_income": total_income,
        "total_expense": total_expense,
    }

    # ✅ Return as Pydantic object
    summary_response = SummaryResponse(**response_data)
    return summary_response

# ---------------- Summary by Subcategory ----------------
def get_summary_by_subcategory(user_id: int, filter_schema: TransactionFilterSchema, month: Optional[int] = None, year: Optional[int] = None):
    tx_type = filter_schema.type
    category_name = filter_schema.category

    query = db.session.query(
        Category.name.label("category"),
        func.sum(Transaction.amount).label("total")
    ).join(Category).filter(Transaction.user_id == user_id)

    # Filter by transaction type
    if tx_type in ("income", "expense"):
        query = query.filter(Transaction.type == tx_type)

    # Filter by category/subcategory
    if category_name:
        query = query.filter(Category.name.ilike(category_name))

    # Filter by month/year if provided
    if month and year:
        query = query.filter(
            extract("month", Transaction.created_date) == month,
            extract("year", Transaction.created_date) == year
        )
    elif year:
        query = query.filter(extract("year", Transaction.created_date) == year)
    elif filter_schema.start_date and filter_schema.end_date:
        query = query.filter(Transaction.created_date.between(filter_schema.start_date, filter_schema.end_date))

    results = query.group_by(Category.name).all()

    return {
        "type": tx_type or "all",
        "subcategory": category_name,
        "summary": [
            {"category": r.category, "total": float(r.total)} for r in results
        ]
    }
