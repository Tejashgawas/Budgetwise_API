from datetime import datetime
from app.services.summary_services import SummaryService
from app.extensions import db
from app.models.transaction import Transaction
from app.models.category import Category
from sqlalchemy import func, extract, case, and_


# Get current year and month
now = datetime.now()
current_year = now.year
current_month = now.month


class Extras:
    @staticmethod
    def calculateDifference(user_id: int):
        now = datetime.now()
        current_year = now.year
        current_month = now.month

        #✅ Get current month total
        total_expenses_current_month = (
            db.session.query(func.sum(Transaction.amount))
            .join(Category)
            .filter(Transaction.user_id == user_id)
            .filter(Category.type == "expense")
            .filter(extract('year', Transaction.created_date) == current_year)
            .filter(extract('month', Transaction.created_date) == current_month)
            .scalar()
        ) or 0.0

        # ✅ Get previous month and handle year wrap-around
        prev_year = current_year if current_month > 1 else current_year - 1
        prev_month = current_month - 1 if current_month > 1 else 12

        # ✅ Get previous month total
        total_expenses_previous_month = (
            db.session.query(func.sum(Transaction.amount))
            .join(Category)
            .filter(Transaction.user_id == user_id)
            .filter(Category.type == "expense")
            .filter(extract('year', Transaction.created_date) == prev_year)
            .filter(extract('month', Transaction.created_date) == prev_month)
            .scalar()
        ) or 0.0

        # total_expenses_previous_month = 15000
        # total_expenses_current_month = 19000

        # ✅ Convert both to float safely (handles Decimal or None)
        total_expenses_current_month = float(total_expenses_current_month)
        total_expenses_previous_month = float(total_expenses_previous_month)

        print(total_expenses_current_month, type(total_expenses_current_month))
        print(total_expenses_previous_month, type(total_expenses_previous_month))

        # ✅ Calculate difference
        # difference = round(total_expenses_current_month - total_expenses_previous_month, 2)
        difference = round(total_expenses_current_month - total_expenses_previous_month, 2)

        percent_change = 0.0
        if total_expenses_previous_month != 0:
            percent_change = round(
                ((total_expenses_current_month - total_expenses_previous_month) / abs(total_expenses_previous_month)) * 100,
                2
            )

        # ✅ Generate statement
        if percent_change > 0:
            statement = f"Your expenses increased by {percent_change}% compared to last month."
        elif percent_change < 0:
            statement = f"Your expenses decreased by {abs(percent_change)}% compared to last month."
        else:
            statement = "Your expenses remained the same as last month."

        return {
            "current_total": total_expenses_current_month,
            "previous_total": total_expenses_previous_month,
            "difference": difference,
            "percent_change": percent_change,
            "statement": statement
        }