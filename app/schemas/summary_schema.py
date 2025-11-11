from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from decimal import Decimal


# -------------------------------------------------------------------------
class CategorySummary(BaseModel):
    """Represents a single category’s summary with total amount."""
    category: Optional[str] = Field(None, description="Name of the category")
    total: Optional[float] = Field(0.0, ge=0, description="Total amount for this category")


# -------------------------------------------------------------------------
class SummaryResponse(BaseModel):
    """
    Response model for summary by period (year, month, or date range).
    Does NOT include breakdowns — used for /period endpoint.
    """

    # Basic info
    type: Optional[str] = Field("all", description="income / expense / all")
    transactions_count: Optional[int] = Field(0, ge=0, description="Total number of transactions")

    # Optional range & context
    range_start: Optional[str] = Field(None, description="Start date of the selected range (as string)")
    range_end: Optional[str] = Field(None, description="End date of the selected range (as string)")
    # subcategory: Optional[str] = Field("All", description="If filtered by subcategory, name of it")

    # Financial totals
    income_transaction_count: Optional[int] = Field(0, description="Number of income transactions")
    income_transaction_total: Optional[float] = Field(0.0, description="Total of all income transactions")
    expense_transaction_count: Optional[int] = Field(0, description="Number of expense transactions")
    expense_transaction_total: Optional[float] = Field(0.0, description="Total of all expense transactions")
    net_difference: Optional[float] = Field(0.0, description="Income - Expense difference")


# -------------------------------------------------------------------------
class SummaryResponseSubCategory(BaseModel):
    """
    Response model for subcategory-based summaries.
    Returns category-level breakdown and total summaries.
    """

    type: Optional[str] = Field("all", description="income / expense / all")
    transactions_count: Optional[int] = Field(0, ge=0, description="Total number of transactions in the selected range")

    # Optional range & context
    range_start: Optional[str] = Field(None, description="Start date of selected range")
    range_end: Optional[str] = Field(None, description="End date of selected range")
    subcategory: Optional[str] = Field("All", description="Filter applied for specific subcategory")

    # Financial totals
    total_income: Optional[Decimal] = Field(Decimal(0), description="Total income amount in this range")
    total_expense: Optional[Decimal] = Field(Decimal(0), description="Total expense amount in this range")
    net_difference: Optional[Decimal] = Field(Decimal(0), description="Difference between income and expense")

    # Breakdown only here
    summary_breakdown: Dict[str, List[CategorySummary]] = Field(
        default_factory=dict,
        description="Detailed breakdown of income and expense categories"
    )
