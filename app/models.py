from datetime import date
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Category(str, Enum):
    groceries = "groceries"
    rent = "rent"
    salary = "salary"
    bills = "bills"
    fun = "fun"
    other = "other"


class TransactionCreate(BaseModel):
    date: date
    amount: float
    merchant: str
    category: Category
    notes: Optional[str] = None


class Transaction(TransactionCreate):
    id: UUID = Field(default_factory=uuid4)


class GoalCreate(BaseModel):
    name: str
    target_amount: float
    monthly_contribution: float
    start_date: date


class Goal(GoalCreate):
    id: UUID = Field(default_factory=uuid4)
