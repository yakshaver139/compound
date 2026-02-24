from datetime import date
from typing import Optional

from fastapi import APIRouter, Query

from app.models import Summary, Transaction, compute_summary
from app.storage import load_data

router = APIRouter(prefix="/summary", tags=["summary"])


@router.get("", response_model=Summary)
def get_summary(
    from_date: Optional[date] = Query(None, alias="from"),
    to_date: Optional[date] = Query(None, alias="to"),
):
    data = load_data()
    txns = data["transactions"]

    if from_date is not None:
        txns = [t for t in txns if date.fromisoformat(t["date"]) >= from_date]
    if to_date is not None:
        txns = [t for t in txns if date.fromisoformat(t["date"]) <= to_date]

    transactions = [Transaction(**t) for t in txns]
    return compute_summary(transactions)
