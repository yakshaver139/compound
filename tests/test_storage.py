import json
from datetime import date
from pathlib import Path

import pytest

from app.models import Category, Goal, Transaction
from app import storage


@pytest.fixture(autouse=True)
def isolated_data_dir(tmp_path, monkeypatch):
    """Point storage at a temp directory for every test."""
    data_dir = tmp_path / "data"
    data_file = data_dir / "compound.json"
    monkeypatch.setattr(storage, "DATA_DIR", data_dir)
    monkeypatch.setattr(storage, "DATA_FILE", data_file)
    return data_dir


class TestLoadData:
    def test_creates_file_when_missing(self, isolated_data_dir):
        data = storage.load_data()
        assert data == {"transactions": [], "goals": []}
        assert (isolated_data_dir / "compound.json").exists()

    def test_reads_existing_file(self, isolated_data_dir):
        isolated_data_dir.mkdir(parents=True)
        payload = {"transactions": [{"x": 1}], "goals": []}
        (isolated_data_dir / "compound.json").write_text(json.dumps(payload))
        assert storage.load_data() == payload


class TestSaveData:
    def test_writes_json(self, isolated_data_dir):
        data = {"transactions": [], "goals": [{"name": "test"}]}
        storage.save_data(data)
        raw = json.loads((isolated_data_dir / "compound.json").read_text())
        assert raw == data

    def test_overwrites_existing(self, isolated_data_dir):
        storage.save_data({"transactions": [], "goals": []})
        storage.save_data({"transactions": [{"a": 1}], "goals": []})
        raw = json.loads((isolated_data_dir / "compound.json").read_text())
        assert len(raw["transactions"]) == 1


class TestAppendTransaction:
    def test_appends_to_empty(self, isolated_data_dir):
        tx = Transaction(
            date=date(2025, 1, 15),
            amount=-42.50,
            merchant="Whole Foods",
            category=Category.groceries,
        )
        storage.append_transaction(tx)
        data = storage.load_data()
        assert len(data["transactions"]) == 1
        assert data["transactions"][0]["merchant"] == "Whole Foods"

    def test_appends_multiple(self, isolated_data_dir):
        for i in range(3):
            tx = Transaction(
                date=date(2025, 1, i + 1),
                amount=-10.0,
                merchant=f"Store {i}",
                category=Category.other,
            )
            storage.append_transaction(tx)
        data = storage.load_data()
        assert len(data["transactions"]) == 3


class TestAppendGoal:
    def test_appends_goal(self, isolated_data_dir):
        goal = Goal(
            name="Emergency Fund",
            target_amount=10000.0,
            monthly_contribution=500.0,
            start_date=date(2025, 1, 1),
        )
        storage.append_goal(goal)
        data = storage.load_data()
        assert len(data["goals"]) == 1
        assert data["goals"][0]["name"] == "Emergency Fund"

    def test_goals_and_transactions_independent(self, isolated_data_dir):
        tx = Transaction(
            date=date(2025, 1, 1),
            amount=-5.0,
            merchant="X",
            category=Category.other,
        )
        goal = Goal(
            name="G",
            target_amount=100.0,
            monthly_contribution=10.0,
            start_date=date(2025, 1, 1),
        )
        storage.append_transaction(tx)
        storage.append_goal(goal)
        data = storage.load_data()
        assert len(data["transactions"]) == 1
        assert len(data["goals"]) == 1
