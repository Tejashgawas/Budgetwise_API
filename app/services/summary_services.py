from app.models.transaction import Transaction
from app.models.category import Category
from app.extensions import db
from sqlalchemy import func, extract
from app.schemas.transaction_schemas import TransactionFilterSchema
from app.schemas.summary_schema import CategorySummary, SummaryResponse, SummaryResponseSubCategory
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
    tx_type: Optional[str] = None,
    start_date: Optional[str] = None,  # from URL (e.g. "2025-10-01")
    end_date: Optional[str] = None     # from URL (e.g. "2025-10-30")
):
    """
    Generate a transaction summary for a user filtered by optional:
    - period_type (month/year)
    - period_value (e.g. "2025-10")
    - start_date & end_date (date range override)
    - tx_type ("income"/"expense")
    """

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

    # 🗓️ Date filtering
    range_start, range_end = None, None

    # ✅ If start_date and end_date provided in URL, use them directly
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
        # Fallback to period-based filtering
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

    # 🧾 Construct response data
    response_data = {
        "type": tx_type or "all",
        "period": period_value,
        "start_date": range_start,
        "end_date": range_end,
        "transactions_count": len(results),  # ✅ fixed key name to match schema
        "total_income": total_income,
        "total_expense": total_expense,
        # include summary if your schema expects it
        # "summary": summary,
    }


    # ✅ Return as Pydantic object
    summary_response = SummaryResponse(**response_data)
    return summary_response

# ---------------- Summary by Subcategory ----------------

def get_summary_by_subcategory(
    user_id: int,
    period_type: Optional[str] = None,
    period_value: Optional[str] = None,
    tx_type: Optional[str] = None,
    start_date: Optional[str] = None,  # from URL (e.g. "2025-10-01")
    end_date: Optional[str] = None,     # from URL (e.g. "2025-10-30")
    category_name: Optional[str] = None  # ✅ new optional filter
):
    """
    Generate a transaction summary for a user filtered by optional:
    - period_type (month/year)
    - period_value (e.g. "2025-10")
    - start_date & end_date (date range override)
    - tx_type ("income"/"expense")
    - category_name (applied after query results)
    """

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

    # 🗓️ Date filtering
    range_start, range_end = None, None

    # ✅ If start_date and end_date provided in URL, use them directly
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
        # Fallback to period-based filtering
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

    # 💰 Filter by transaction type if provided
    if tx_type in ("income", "expense"):
        query = query.filter(Transaction.type == tx_type)

    # 🧮 Execute query (keep all results)
    results = query.group_by(Category.id, Category.name, Category.type).all()

    # ✅ Now apply category_name filtering *after* fetching results
    if category_name:
        results = [r for r in results if r.category_name.lower() == category_name.lower()]

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
    
    print(summary)

    # 🧾 Construct response data
    response_data = {
        "type": tx_type or "all",
        "period": period_value,
        "start_date": range_start,
        "end_date": range_end,
        "transactions_count": len(results),
        "total_income": total_income,
        "total_expense": total_expense,
        # include summary if needed
        "summary": summary,
    }

    # ✅ Return as Pydantic object
    summary_response = SummaryResponseSubCategory(**response_data)
    return summary_response
