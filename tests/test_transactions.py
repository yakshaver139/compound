from datetime import date
from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from app import storage
from app.main import app
from app.models import Category, Transaction

client = TestClient(app)


@pytest.fixture(autouse=True)
def isolated_data_dir(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    data_file = data_dir / "compound.json"
    monkeypatch.setattr(storage, "DATA_DIR", data_dir)
    monkeypatch.setattr(storage, "DATA_FILE", data_file)
    return data_dir


def _seed(transactions: list[Transaction]) -> None:
    for tx in transactions:
        storage.append_transaction(tx)


TXNS = [
    Transaction(
        date=date(2025, 1, 10),
        amount=-50.0,
        merchant="Whole Foods",
        category=Category.groceries,
    ),
    Transaction(
        date=date(2025, 1, 20),
        amount=-1200.0,
        merchant="Landlord",
        category=Category.rent,
    ),
    Transaction(
        date=date(2025, 2, 5),
        amount=3000.0,
        merchant="Employer",
        category=Category.salary,
    ),
]


class TestListTransactions:
    def test_empty(self):
        resp = client.get("/transactions")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_returns_all_most_recent_first(self):
        _seed(TXNS)
        resp = client.get("/transactions")
        assert resp.status_code == 200
        items = resp.json()
        assert len(items) == 3
        dates = [t["date"] for t in items]
        assert dates == ["2025-02-05", "2025-01-20", "2025-01-10"]

    def test_filter_from(self):
        _seed(TXNS)
        resp = client.get("/transactions", params={"from": "2025-01-15"})
        items = resp.json()
        assert len(items) == 2
        assert all(t["date"] >= "2025-01-15" for t in items)

    def test_filter_to(self):
        _seed(TXNS)
        resp = client.get("/transactions", params={"to": "2025-01-20"})
        items = resp.json()
        assert len(items) == 2
        assert all(t["date"] <= "2025-01-20" for t in items)

    def test_filter_from_and_to(self):
        _seed(TXNS)
        resp = client.get(
            "/transactions", params={"from": "2025-01-15", "to": "2025-01-25"}
        )
        items = resp.json()
        assert len(items) == 1
        assert items[0]["merchant"] == "Landlord"

    def test_filter_category(self):
        _seed(TXNS)
        resp = client.get("/transactions", params={"category": "groceries"})
        items = resp.json()
        assert len(items) == 1
        assert items[0]["category"] == "groceries"

    def test_filter_category_no_match(self):
        _seed(TXNS)
        resp = client.get("/transactions", params={"category": "fun"})
        assert resp.json() == []

    def test_filter_combined(self):
        _seed(TXNS)
        resp = client.get(
            "/transactions",
            params={"from": "2025-01-01", "to": "2025-01-31", "category": "rent"},
        )
        items = resp.json()
        assert len(items) == 1
        assert items[0]["merchant"] == "Landlord"

    def test_invalid_category_returns_422(self):
        resp = client.get("/transactions", params={"category": "invalid"})
        assert resp.status_code == 422

    def test_response_contains_transaction_fields(self):
        _seed(TXNS[:1])
        resp = client.get("/transactions")
        item = resp.json()[0]
        assert "id" in item
        assert "date" in item
        assert "amount" in item
        assert "merchant" in item
        assert "category" in item
class TestPostTransaction:
    def test_create_returns_201(self):
        resp = client.post("/transactions", json={
            "date": "2025-03-15",
            "amount": -42.50,
            "merchant": "Whole Foods",
            "category": "groceries",
        })
        assert resp.status_code == 201

    def test_create_returns_transaction_with_id(self):
        resp = client.post("/transactions", json={
            "date": "2025-03-15",
            "amount": -42.50,
            "merchant": "Whole Foods",
            "category": "groceries",
        })
        body = resp.json()
        assert UUID(body["id"])
        assert body["date"] == "2025-03-15"
        assert body["amount"] == -42.50
        assert body["merchant"] == "Whole Foods"
        assert body["category"] == "groceries"

    def test_create_persists_to_store(self):
        client.post("/transactions", json={
            "date": "2025-01-01",
            "amount": 3000.0,
            "merchant": "Employer",
            "category": "salary",
        })
        data = storage.load_data()
        assert len(data["transactions"]) == 1
        assert data["transactions"][0]["merchant"] == "Employer"

    def test_category_defaults_to_other(self):
        resp = client.post("/transactions", json={
            "date": "2025-06-01",
            "amount": -9.99,
            "merchant": "Random Shop",
        })
        assert resp.status_code == 201
        assert resp.json()["category"] == "other"

    def test_notes_optional(self):
        resp = client.post("/transactions", json={
            "date": "2025-06-01",
            "amount": -5.0,
            "merchant": "Cafe",
            "category": "fun",
            "notes": "Latte",
        })
        assert resp.json()["notes"] == "Latte"

    def test_invalid_date_rejected(self):
        resp = client.post("/transactions", json={
            "date": "not-a-date",
            "amount": -10.0,
            "merchant": "X",
        })
        assert resp.status_code == 422

    def test_missing_amount_rejected(self):
        resp = client.post("/transactions", json={
            "date": "2025-01-01",
            "merchant": "X",
        })
        assert resp.status_code == 422

    def test_missing_merchant_rejected(self):
        resp = client.post("/transactions", json={
            "date": "2025-01-01",
            "amount": -10.0,
        })
        assert resp.status_code == 422

    def test_invalid_category_rejected(self):
        resp = client.post("/transactions", json={
            "date": "2025-01-01",
            "amount": -10.0,
            "merchant": "X",
            "category": "nonexistent",
        })
        assert resp.status_code == 422
