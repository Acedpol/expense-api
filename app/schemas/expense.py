from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ExpenseCreate(BaseModel):
    amount: float
    description: str
    date: date
    category_id: int


class ExpenseUpdate(BaseModel):
    amount: Optional[float] = None
    description: Optional[str] = None
    date: Optional[date] = None
    category_id: Optional[int] = None


class ExpenseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    amount: float
    description: str
    date: date
    category_id: int
