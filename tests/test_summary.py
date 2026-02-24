from datetime import date

import pytest
from fastapi.testclient import TestClient

from app import storage
from app.main import app
from app.models import Category, Transaction, Summary, compute_summary

client = TestClient(app)


def _tx(amount: float, category: Category = Category.other, d: date = date(2025, 1, 15)) -> Transaction:
    return Transaction(date=d, amount=amount, merchant="test", category=category)


# ── Unit tests for compute_summary ──────────────────────────────────────


def test_empty_transactions():
    result = compute_summary([])
    assert result == Summary(
        total_income=0.0,
        total_expense=0.0,
        net=0.0,
        spend_by_category={},
        monthly_net={},
    )


def test_income_only():
    result = compute_summary([_tx(1000, Category.salary)])
    assert result.total_income == 1000.0
    assert result.total_expense == 0.0
    assert result.net == 1000.0
    assert result.spend_by_category == {}


def test_expense_only():
    result = compute_summary([_tx(-50, Category.groceries)])
    assert result.total_income == 0.0
    assert result.total_expense == 50.0
    assert result.net == -50.0
    assert result.spend_by_category == {"groceries": 50.0}


def test_mixed_transactions():
    txs = [
        _tx(3000, Category.salary),
        _tx(-800, Category.rent),
        _tx(-150, Category.groceries),
        _tx(-50, Category.fun),
    ]
    result = compute_summary(txs)
    assert result.total_income == 3000.0
    assert result.total_expense == 1000.0
    assert result.net == 2000.0
    assert result.spend_by_category == {"rent": 800.0, "groceries": 150.0, "fun": 50.0}


def test_spend_by_category_aggregates():
    txs = [
        _tx(-20, Category.groceries),
        _tx(-30, Category.groceries),
        _tx(-10, Category.fun),
    ]
    result = compute_summary(txs)
    assert result.spend_by_category == {"groceries": 50.0, "fun": 10.0}


def test_monthly_net():
    txs = [
        _tx(3000, Category.salary, date(2025, 1, 1)),
        _tx(-500, Category.rent, date(2025, 1, 15)),
        _tx(3000, Category.salary, date(2025, 2, 1)),
        _tx(-600, Category.rent, date(2025, 2, 15)),
    ]
    result = compute_summary(txs)
    assert result.monthly_net == {"2025-01": 2500.0, "2025-02": 2400.0}


def test_rounding():
    txs = [_tx(10.1), _tx(10.2), _tx(-5.15)]
    result = compute_summary(txs)
    assert result.total_income == 20.3
    assert result.total_expense == 5.15
    assert result.net == 15.15


# ── Endpoint tests for GET /summary ────────────────────────────────────


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


class TestGetSummary:
    def test_empty(self):
        resp = client.get("/summary")
        assert resp.status_code == 200
        body = resp.json()
        assert body["total_income"] == 0.0
        assert body["total_expense"] == 0.0
        assert body["net"] == 0.0
        assert body["spend_by_category"] == {}

    def test_all_transactions(self):
        _seed(TXNS)
        resp = client.get("/summary")
        assert resp.status_code == 200
        body = resp.json()
        assert body["total_income"] == 3000.0
        assert body["total_expense"] == 1250.0
        assert body["net"] == 1750.0
        assert body["spend_by_category"] == {"groceries": 50.0, "rent": 1200.0}

    def test_filter_from(self):
        _seed(TXNS)
        resp = client.get("/summary", params={"from": "2025-01-15"})
        assert resp.status_code == 200
        body = resp.json()
        # Only Landlord (-1200) and Employer (+3000) included
        assert body["total_income"] == 3000.0
        assert body["total_expense"] == 1200.0
        assert body["net"] == 1800.0
        assert body["spend_by_category"] == {"rent": 1200.0}

    def test_filter_to(self):
        _seed(TXNS)
        resp = client.get("/summary", params={"to": "2025-01-31"})
        assert resp.status_code == 200
        body = resp.json()
        # Only Whole Foods (-50) and Landlord (-1200) included
        assert body["total_income"] == 0.0
        assert body["total_expense"] == 1250.0
        assert body["net"] == -1250.0

    def test_filter_from_and_to(self):
        _seed(TXNS)
        resp = client.get("/summary", params={"from": "2025-01-15", "to": "2025-01-25"})
        assert resp.status_code == 200
        body = resp.json()
        # Only Landlord (-1200)
        assert body["total_income"] == 0.0
        assert body["total_expense"] == 1200.0
        assert body["net"] == -1200.0
        assert body["spend_by_category"] == {"rent": 1200.0}

    def test_filter_no_match(self):
        _seed(TXNS)
        resp = client.get("/summary", params={"from": "2026-01-01"})
        assert resp.status_code == 200
        body = resp.json()
        assert body["total_income"] == 0.0
        assert body["total_expense"] == 0.0
        assert body["net"] == 0.0

    def test_response_has_monthly_net(self):
        _seed(TXNS)
        resp = client.get("/summary")
        body = resp.json()
        assert "2025-01" in body["monthly_net"]
        assert "2025-02" in body["monthly_net"]
        assert body["monthly_net"]["2025-01"] == -1250.0
        assert body["monthly_net"]["2025-02"] == 3000.0
