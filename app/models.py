import math
from collections import defaultdict
from datetime import date
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from dateutil.relativedelta import relativedelta
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
    category: Category = Category.other
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


class GoalProjection(BaseModel):
    months_to_target: int
    target_date: date


class GoalWithProjection(Goal):
    projection: GoalProjection


def compute_projection(goal: Goal) -> GoalProjection:
    """Compute simple projection for a goal."""
    if goal.monthly_contribution <= 0:
        return GoalProjection(
            months_to_target=0,
            target_date=goal.start_date,
        )
    months = math.ceil(goal.target_amount / goal.monthly_contribution)
    target_date = goal.start_date + relativedelta(months=months)
    return GoalProjection(months_to_target=months, target_date=target_date)


class Summary(BaseModel):
    total_income: float
    total_expense: float
    net: float
    spend_by_category: dict[str, float]
    monthly_net: dict[str, float]


def compute_summary(transactions: list[Transaction]) -> Summary:
    """Pure function: compute summary statistics from a list of transactions."""
    total_income = 0.0
    total_expense = 0.0
    spend_by_cat: dict[str, float] = defaultdict(float)
    monthly: dict[str, float] = defaultdict(float)

    for tx in transactions:
        amt = tx.amount
        if amt > 0:
            total_income += amt
        else:
            total_expense += abs(amt)
            spend_by_cat[tx.category.value] += abs(amt)
        monthly[tx.date.strftime("%Y-%m")] += amt

    return Summary(
        total_income=round(total_income, 2),
        total_expense=round(total_expense, 2),
        net=round(total_income - total_expense, 2),
        spend_by_category=dict(spend_by_cat),
        monthly_net=dict(monthly),
    )
