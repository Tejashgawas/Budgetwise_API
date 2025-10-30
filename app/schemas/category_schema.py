from pydantic import BaseModel, Field
from typing import Optional


class CategoryCreateSchema(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    type: str = Field(..., pattern="^(income|expense)$")


class CategoryResponseSchema(BaseModel):
    id: int
    name: str
    type: str

    class Config:
        from_attributes = True

class CategoryUpdateSchema(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None