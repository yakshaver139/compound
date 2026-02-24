from datetime import date
from typing import Optional

from fastapi import APIRouter, Query

from app.models import Category, Transaction
from app.storage import load_data

from app.models import Transaction, TransactionCreate
from app.storage import append_transaction

from app.models import Transaction, TransactionCreate
from app.storage import append_transaction

router = APIRouter(prefix="/transactions", tags=["transactions"])

@router.get("", response_model=list[Transaction])
def list_transactions(
    from_date: Optional[date] = Query(None, alias="from"),
    to_date: Optional[date] = Query(None, alias="to"),
    category: Optional[Category] = None,
) -> list[dict]:
    data = load_data()
    txns = data["transactions"]

    if from_date is not None:
        txns = [t for t in txns if date.fromisoformat(t["date"]) >= from_date]
    if to_date is not None:
        txns = [t for t in txns if date.fromisoformat(t["date"]) <= to_date]
    if category is not None:
        txns = [t for t in txns if t["category"] == category.value]

    txns.sort(key=lambda t: t["date"], reverse=True)
    return txns

@router.post("", status_code=201)
def create_transaction(body: TransactionCreate) -> Transaction:
    tx = Transaction(**body.model_dump())
    append_transaction(tx)
    return tx
