from app.models.transaction import Transaction
from app.models.category import Category
from app.extensions import db
from sqlalchemy import func, extract
from app.schemas.transaction_schemas import TransactionFilterSchema
from app.schemas.summary_schema import CategorySummary, SummaryResponse
from datetime import date
from typing import Dict, List, Optional

# ---------------- Summary by Period ----------------
def get_summary_by_period(user_id: int, period_type: str, period_value: Optional[str], tx_type: Optional[str] = None):
    query = db.session.query(
        Category.name.label("category"),
        Category.type.label("category_type"),
        func.sum(Transaction.amount).label("total")
    ).join(Category).filter(Transaction.user_id == user_id)

    # Filter by period
    start_date = None
    end_date = None
    if period_type == "month" and period_value:
        year, month = map(int, period_value.split("-"))
        query = query.filter(
            extract("year", Transaction.created_date) == year,
            extract("month", Transaction.created_date) == month
        )
        # For display in schema, optional: start/end date of month
        start_date = date(year, month, 1)
        # end_date = last day of month (simplified)
        import calendar
        end_date = date(year, month, calendar.monthrange(year, month)[1])
    elif period_type == "year" and period_value:
        year = int(period_value)
        query = query.filter(extract("year", Transaction.created_date) == year)
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)

    # Filter by type if provided
    if tx_type in ("income", "expense"):
        query = query.filter(Transaction.type == tx_type)

    results = query.group_by(Category.id, Category.name, Category.type).all()
    print("Fetched Data=>",results)
    # Build summary dict with CategorySummary objects
    summary: Dict[str, List[CategorySummary]] = {}
    for r in results:
        summary.setdefault(r.category_type  , []).append(
            CategorySummary(category=r.category, total=float(r.total))
        )

        response_data = {
        "type": tx_type or "all",
        "summary": summary
    }

    # 2️⃣ Add optional fields only if they exist
    if period_type:
        response_data["period_type"] = period_type
    if period_value:
        response_data["period"] = period_value
    if start_date and end_date:
        response_data["start_date"] = start_date
        response_data["end_date"] = end_date
    # subcategory is not applicable for period summary

    # 3️⃣ Create the Pydantic object
    summary_response = SummaryResponse(**response_data)

    return summary_response


# ---------------- Summary by Date Range ----------------
def get_summary_by_date_range(user_id: int, filter_schema: TransactionFilterSchema):
    tx_type = filter_schema.type
    start = filter_schema.start_date
    end = filter_schema.end_date

    query = db.session.query(
        Category.name.label("category"),
        Category.type.label("category_type"),
        func.sum(Transaction.amount).label("total")
    ).join(Category).filter(Transaction.user_id == user_id)

    if start and end:
        query = query.filter(Transaction.created_date.between(start, end))

    if tx_type in ("income", "expense"):
        query = query.filter(Transaction.type == tx_type)

    results = query.group_by(Category.id, Category.name, Category.type).all()

    summary = {}
    for r in results:
        summary.setdefault(r.category_type, []).append({
            "category": r.category,
            "total": float(r.total)
        })

    return {
        "type": tx_type or "all",
        "start_date": start,
        "end_date": end,
        "summary": summary
    }

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
