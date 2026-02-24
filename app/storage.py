import json
import os
import tempfile
from pathlib import Path

from app.models import Goal, Transaction

DATA_DIR = Path("data")
DATA_FILE = DATA_DIR / "compound.json"

EMPTY_DATA = {"transactions": [], "goals": []}


def load_data() -> dict:
    """Load data from JSON file, creating it if missing."""
    if not DATA_FILE.exists():
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        save_data(EMPTY_DATA)
        return {"transactions": [], "goals": []}
    with open(DATA_FILE) as f:
        return json.load(f)


def save_data(data: dict) -> None:
    """Atomically write data to JSON file."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=DATA_DIR, suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(data, f, indent=2, default=str)
            f.write("\n")
        os.replace(tmp_path, DATA_FILE)
    except BaseException:
        os.unlink(tmp_path)
        raise


def append_transaction(tx: Transaction) -> None:
    """Add a transaction to the store."""
    data = load_data()
    data["transactions"].append(tx.model_dump(mode="json"))
    save_data(data)


def append_goal(goal: Goal) -> None:
    """Add a goal to the store."""
    data = load_data()
    data["goals"].append(goal.model_dump(mode="json"))
    save_data(data)
