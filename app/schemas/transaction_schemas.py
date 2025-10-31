from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import date as dt_date
from decimal import Decimal

class TransactionCreateSchema(BaseModel):
    amount: Decimal
    type: str  # "income" or "expense"
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    description: Optional[str] = None
    date: Optional[dt_date] = None

    @field_validator("type")
    def validate_type(cls, value):
        if value not in ("income", "expense"):
            raise ValueError("type must be either 'income' or 'expense'")
        return value
    

class TransactionUpdateSchema(BaseModel):
    amount: Optional[Decimal] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    date: Optional[dt_date] = None

class TransactionResponseSchema(BaseModel):
    id: int
    amount: Decimal
    type: str
    category: str
    description: Optional[str]
    date: dt_date
    user_id: int

    class Config:
        from_attributes = True

class TransactionFilterSchema(BaseModel):
    type: Optional[str] = None
    category: Optional[str] = None
    start_date: Optional[dt_date] = None
    end_date: Optional[dt_date] = None
    page: Optional[int] = 1
    per_page: Optional[int] = 10