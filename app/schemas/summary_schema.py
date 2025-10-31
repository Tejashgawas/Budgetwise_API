from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from decimal import Decimal
from datetime import date

class CategorySummary(BaseModel):
    category: str
    total: float = Field(..., ge=0, description="Total amount for this category")

class SummaryResponse(BaseModel):
    type: str = Field(..., description="income / expense / all")
    period: Optional[str] = Field(None, description="Month or Year if applicable")
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    transactions_count: int = Field(..., ge=0, description="Total number of transactions")
    # summary: Dict[str, List[CategorySummary]]
    # summary: Dict[str, List[CategorySummary]] = Field(
    #     default_factory=dict,
    #     description="Summary grouped by category type (income, expense)"
    # )
    total_expense : Optional[Decimal] = None
    total_income : Optional[Decimal] = None

class SummaryResponseSubCategory(BaseModel):
    type: str = Field(..., description="income / expense / all")
    period: Optional[str] = Field(None, description="Month or Year if applicable")
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    transactions_count: int = Field(..., ge=0, description="Total number of transactions")
    summary: Dict[str, List[CategorySummary]]
    # summary: Dict[str, List[CategorySummary]] = Field(
    #     default_factory=dict,
    #     description="Summary grouped by category type (income, expense)"
    # )
    total_expense : Optional[Decimal] = None
    total_income : Optional[Decimal] = None
    
    
