from datetime import date
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class TransactionCreate(BaseModel):
    date: date
    amount: float
    merchant: str
    category: str
    notes: str = ""


class Transaction(TransactionCreate):
    id: UUID = Field(default_factory=uuid4)


class GoalCreate(BaseModel):
    name: str
    target_amount: float
    monthly_contribution: float
    start_date: date


class Goal(GoalCreate):
    id: UUID = Field(default_factory=uuid4)
