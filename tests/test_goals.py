from datetime import date
from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from app import storage
from app.main import app
from app.models import Goal

client = TestClient(app)


@pytest.fixture(autouse=True)
def isolated_data_dir(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    data_file = data_dir / "compound.json"
    monkeypatch.setattr(storage, "DATA_DIR", data_dir)
    monkeypatch.setattr(storage, "DATA_FILE", data_file)
    return data_dir


class TestListGoals:
    def test_empty(self):
        resp = client.get("/goals")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_returns_goals_with_projection(self):
        storage.append_goal(
            Goal(
                name="Emergency Fund",
                target_amount=10000.0,
                monthly_contribution=500.0,
                start_date=date(2025, 1, 1),
            )
        )
        resp = client.get("/goals")
        assert resp.status_code == 200
        items = resp.json()
        assert len(items) == 1
        item = items[0]
        assert item["name"] == "Emergency Fund"
        assert "projection" in item
        assert item["projection"]["months_to_target"] == 20
        assert item["projection"]["target_date"] == "2026-09-01"


class TestPostGoal:
    def test_create_returns_201(self):
        resp = client.post("/goals", json={
            "name": "Vacation",
            "target_amount": 5000.0,
            "monthly_contribution": 200.0,
            "start_date": "2025-06-01",
        })
        assert resp.status_code == 201

    def test_create_returns_goal_with_projection(self):
        resp = client.post("/goals", json={
            "name": "Vacation",
            "target_amount": 5000.0,
            "monthly_contribution": 200.0,
            "start_date": "2025-06-01",
        })
        body = resp.json()
        assert UUID(body["id"])
        assert body["name"] == "Vacation"
        assert body["projection"]["months_to_target"] == 25
        assert body["projection"]["target_date"] == "2027-07-01"

    def test_create_persists_to_store(self):
        client.post("/goals", json={
            "name": "Car",
            "target_amount": 20000.0,
            "monthly_contribution": 1000.0,
            "start_date": "2025-01-01",
        })
        data = storage.load_data()
        assert len(data["goals"]) == 1
        assert data["goals"][0]["name"] == "Car"

    def test_zero_contribution_safe(self):
        resp = client.post("/goals", json={
            "name": "Someday",
            "target_amount": 10000.0,
            "monthly_contribution": 0.0,
            "start_date": "2025-01-01",
        })
        assert resp.status_code == 201
        body = resp.json()
        assert body["projection"]["months_to_target"] == 0

    def test_missing_name_rejected(self):
        resp = client.post("/goals", json={
            "target_amount": 5000.0,
            "monthly_contribution": 200.0,
            "start_date": "2025-01-01",
        })
        assert resp.status_code == 422
