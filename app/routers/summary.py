from fastapi import APIRouter

from app.models import Summary, Transaction, compute_summary
from app.storage import load_data

router = APIRouter(prefix="/summary", tags=["summary"])


@router.get("", response_model=Summary)
def get_summary():
    data = load_data()
    transactions = [Transaction(**t) for t in data["transactions"]]
    return compute_summary(transactions)
