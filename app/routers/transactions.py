from fastapi import APIRouter

from app.models import Transaction, TransactionCreate
from app.storage import append_transaction

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post("", status_code=201)
def create_transaction(body: TransactionCreate) -> Transaction:
    tx = Transaction(**body.model_dump())
    append_transaction(tx)
    return tx
