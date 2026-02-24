from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["ui"])

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"


@router.get("/", response_class=HTMLResponse)
def home():
    html = (TEMPLATES_DIR / "transactions.html").read_text()
    return HTMLResponse(content=html)
