from app.models.transaction import Transaction
from app.models.category import Category
from app.extensions import db
from sqlalchemy import func, extract, case, and_
from app.schemas.summary_schema import SummaryResponse, SummaryResponseSubCategory
from app.utils.summary_exceptions import *
from datetime import date, datetime
from typing import Optional
import calendar



class SummaryService:

    # -------------------------------------------------------------------------
    @staticmethod
    def get_summary_by_period(
        user_id: int,
        period_type: Optional[str] = None,
        tx_type: Optional[str] = None,
        start: Optional[str] = None,
        end: Optional[str] = None,
        caller: Optional[str] = None,
        subcategory: Optional[str] = None,
    ):
        """Get total income, total expense, and transaction counts."""

        try:
            # ---------------------------- VALIDATION ----------------------------
            if not user_id:
                raise MissingParameterError("Missing required parameter: user_id.")

            if not start or not end:
                raise MissingParameterError("Missing required parameters: start and end.")

            if period_type not in ["month", "year", "date"]:
                raise InvalidPeriodTypeError(
                    "Invalid period_type. Must be 'month', 'year', or 'date'."
                )

            # Handle dashboard default (current year)
            if caller == "dashboard":
                period_type = "year"
                start = end = str(datetime.now().year)

            # -------------------------- BUILD FILTER ---------------------------
            filter_condition, range_start, range_end = SummaryService._build_period_filter(
                period_type, start, end, subcategory
            )

            # ----------------------------- QUERY -------------------------------
            query = (
                db.session.query(
                    func.sum(case((Category.type == "expense", 1), else_=0)).label("expense_transaction_count"),
                    func.sum(case((Category.type == "expense", Transaction.amount), else_=0)).label("expense_transaction_total"),
                    func.sum(case((Category.type == "income", 1), else_=0)).label("income_transaction_count"),
                    func.sum(case((Category.type == "income", Transaction.amount), else_=0)).label("income_transaction_total"),
                    func.count(Transaction.id).label("total_transactions"),
                    (
                        func.sum(case((Category.type == "income", Transaction.amount), else_=0))
                        - func.sum(case((Category.type == "expense", Transaction.amount), else_=0))
                    ).label("net_difference"),
                )
                .join(Category)
                .filter(Transaction.user_id == user_id)
                .filter(filter_condition)
            )

            result = query.first()

            if not result or result.total_transactions == 0:
                raise SummaryNotFoundError(
                    f"No transactions found for subcategory '{subcategory}'." if subcategory 
                    else "No transactions found for the selected period."
                )

            # --------------------------- PREPARE SUMMARY ------------------------
            summary = {
                "expense_transaction_count": int(result.expense_transaction_count or 0),
                "expense_transaction_total": float(result.expense_transaction_total or 0),
                "income_transaction_count": int(result.income_transaction_count or 0),
                "income_transaction_total": float(result.income_transaction_total or 0),
                "total_transactions": int(result.total_transactions or 0),
                "net_difference": float(result.net_difference or 0),
                "range_start": str(range_start),
                "range_end": str(range_end),
                "subcategory": subcategory or "All",
            }

            # Filter by tx_type
            if tx_type == "income":
                filtered_summary = {
                    "income_transaction_count": summary["income_transaction_count"],
                    "income_transaction_total": summary["income_transaction_total"],
                    "total_transactions": summary["income_transaction_count"],
                    "range_start": summary["range_start"],
                    "range_end": summary["range_end"],
                }
            elif tx_type == "expense":
                filtered_summary = {
                    "expense_transaction_count": summary["expense_transaction_count"],
                    "expense_transaction_total": summary["expense_transaction_total"],
                    "total_transactions": summary["expense_transaction_count"],
                    "range_start": summary["range_start"],
                    "range_end": summary["range_end"],
                }
            else:
                filtered_summary = summary

            response_payload = {
                **filtered_summary,
                "type": tx_type or "all",
                "transactions_count": filtered_summary.get("total_transactions", 0),
                "range_start": summary["range_start"],
                "range_end": summary["range_end"],
            }

            return SummaryResponse(**response_payload)

        except SummaryError:
            # Directly rethrow custom exceptions
            raise

        except Exception as e:
            raise SummaryDatabaseError(f"Unexpected summary error: {str(e)}")


    # -------------------------------------------------------------------------
    @staticmethod
    def get_summary_by_subcategory(
        user_id: int,
        period_type: Optional[str] = None,
        tx_type: Optional[str] = None,
        start: Optional[str] = None,
        end: Optional[str] = None,
        subcategory: Optional[str] = None,
        caller: Optional[str] = None,
    ):
        """Get subcategory breakdown of income/expense totals."""

        try:
            # ---------------------------- VALIDATION ----------------------------
            if not user_id:
                raise MissingParameterError("Missing required parameter: user_id.")

            if not start or not end:
                raise MissingParameterError("Missing required parameters: start and end.")

            if period_type not in ["month", "year", "date"]:
                raise InvalidPeriodTypeError(
                    "Invalid period_type. Must be 'month', 'year', or 'date'."
                )

            if caller == "dashboard":
                period_type = "year"
                start = end = str(datetime.now().year)

            # -------------------------- BUILD FILTER ---------------------------
            filter_condition, range_start, range_end = SummaryService._build_period_filter(
                period_type, start, end, subcategory
            )

            # ----------------------------- SUMMARY QUERY -----------------------
            query = (
                db.session.query(
                    func.sum(case((Category.type == "expense", 1), else_=0)).label("expense_transaction_count"),
                    func.sum(case((Category.type == "expense", Transaction.amount), else_=0)).label("expense_transaction_total"),
                    func.sum(case((Category.type == "income", 1), else_=0)).label("income_transaction_count"),
                    func.sum(case((Category.type == "income", Transaction.amount), else_=0)).label("income_transaction_total"),
                    func.count(Transaction.id).label("total_transactions"),
                    (
                        func.sum(case((Category.type == "income", Transaction.amount), else_=0))
                        - func.sum(case((Category.type == "expense", Transaction.amount), else_=0))
                    ).label("net_difference"),
                )
                .join(Category)
                .filter(Transaction.user_id == user_id)
                .filter(filter_condition)
            )

            result = query.first()

            if not result or result.total_transactions == 0:
                raise SummaryNotFoundError(
                    "No transactions found for this period or subcategory."
                )

            summary = {
                "expense_transaction_count": int(result.expense_transaction_count or 0),
                "expense_transaction_total": float(result.expense_transaction_total or 0),
                "income_transaction_count": int(result.income_transaction_count or 0),
                "income_transaction_total": float(result.income_transaction_total or 0),
                "total_transactions": int(result.total_transactions or 0),
                "net_difference": float(result.net_difference or 0),
            }

            # ----------------------- TYPE FILTERING ---------------------------
            if tx_type == "income":
                filtered_summary = {
                    "income_transaction_count": summary["income_transaction_count"],
                    "income_transaction_total": summary["income_transaction_total"],
                    "total_transactions": summary["income_transaction_count"],
                }
            elif tx_type == "expense":
                filtered_summary = {
                    "expense_transaction_count": summary["expense_transaction_count"],
                    "expense_transaction_total": summary["expense_transaction_total"],
                    "total_transactions": summary["expense_transaction_count"],
                }
            else:
                filtered_summary = summary

            # ---------------------- SUBCATEGORY BREAKDOWN ----------------------
            breakdown_query = (
                db.session.query(
                    Category.name.label("category_name"),
                    Category.type.label("category_type"),
                    func.sum(Transaction.amount).label("total"),
                )
                .join(Category)
                .filter(Transaction.user_id == user_id)
                .filter(Transaction.created_date.between(range_start, range_end))
                .group_by(Category.name, Category.type)
            )

            if subcategory:
                breakdown_query = breakdown_query.filter(Category.name.ilike(subcategory))

            breakdown_results = breakdown_query.all()

            summary_breakdown = {"income": [], "expense": []}

            for r in breakdown_results:
                # Include ALL categories
                if tx_type is None or tx_type == "all":
                    summary_breakdown[r.category_type].append(
                        {"category": r.category_name, "total": float(r.total)}
                    )

                # Include ONLY income
                elif tx_type == "income" and r.category_type == "income":
                    summary_breakdown["income"].append(
                        {"category": r.category_name, "total": float(r.total)}
                    )

                # Include ONLY expense
                elif tx_type == "expense" and r.category_type == "expense":
                    summary_breakdown["expense"].append(
                        {"category": r.category_name, "total": float(r.total)}
                    )


            response_data = {
                "type": tx_type or "all",
                "transactions_count": filtered_summary.get("total_transactions", 0),
                "range_start": str(range_start),
                "range_end": str(range_end),
                "subcategory": subcategory or "All",
                "total_income": filtered_summary.get("income_transaction_total", 0.0),
                "total_expense": filtered_summary.get("expense_transaction_total", 0.0),
                "net_difference": filtered_summary.get("net_difference", 0.0),
                "summary_breakdown": summary_breakdown,
            }

            return SummaryResponseSubCategory(**response_data)

        except SummaryError:
            raise

        except Exception as e:
            raise SummaryDatabaseError(f"Unexpected summary error: {str(e)}")


    # -------------------------------------------------------------------------
    @staticmethod
    def _build_period_filter(period_type: str, start: str, end: str, subcategory: Optional[str] = None):
        """Builds SQLAlchemy date/month/year filter."""
        print("Building filter for:", period_type, start, end, subcategory)
        try:
            filters = []

            if period_type == "year":
                start_year = int(start)
                end_year = int(end)
                filters.append(extract("year", Transaction.created_date).between(start_year, end_year))
                range_start = date(start_year, 1, 1)
                range_end = date(end_year, 12, 31)

            elif period_type == "month":
                start_year, start_month = map(int, start.split("-"))
                end_year, end_month = map(int, end.split("-"))
                range_start = date(start_year, start_month, 1)
                last_day = calendar.monthrange(end_year, end_month)[1]
                range_end = date(end_year, end_month, last_day)

                filters.append(
                    and_(
                        extract("year", Transaction.created_date).between(start_year, end_year),
                        extract("month", Transaction.created_date).between(start_month, end_month),
                    )
                )

            elif period_type == "date":
                range_start = datetime.strptime(start, "%Y-%m-%d").date()
                range_end = datetime.strptime(end, "%Y-%m-%d").date()
                filters.append(Transaction.created_date.between(range_start, range_end))

            else:
                raise InvalidPeriodTypeError("Invalid period_type supplied.")

            if subcategory:
                filters.append(Category.name.ilike(subcategory))

            return and_(*filters), range_start, range_end

        except ValueError:
            raise InvalidPeriodTypeError("Invalid date or period format.")
        except Exception as e:
            raise SummaryDatabaseError(f"Error building filter: {str(e)}")
