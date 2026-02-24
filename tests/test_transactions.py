from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from app import storage
from app.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def isolated_data_dir(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    data_file = data_dir / "compound.json"
    monkeypatch.setattr(storage, "DATA_DIR", data_dir)
    monkeypatch.setattr(storage, "DATA_FILE", data_file)
    return data_dir


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
