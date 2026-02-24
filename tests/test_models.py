from datetime import date
from uuid import UUID

import pytest
from pydantic import ValidationError

from app.models import Category, Goal, GoalCreate, Transaction, TransactionCreate


class TestTransaction:
    def test_create_transaction(self):
        tx = Transaction(
            date=date(2025, 1, 15),
            amount=-42.50,
            merchant="Whole Foods",
            category=Category.groceries,
        )
        assert isinstance(tx.id, UUID)
        assert tx.date == date(2025, 1, 15)
        assert tx.amount == -42.50
        assert tx.merchant == "Whole Foods"
        assert tx.category == Category.groceries
        assert tx.notes is None

    def test_transaction_with_notes(self):
        tx = Transaction(
            date=date(2025, 1, 15),
            amount=3000.0,
            merchant="Employer",
            category="salary",
            notes="January paycheck",
        )
        assert tx.notes == "January paycheck"

    def test_category_string_coercion(self):
        tx = Transaction(
            date=date(2025, 1, 15),
            amount=-10.0,
            merchant="Netflix",
            category="fun",
        )
        assert tx.category == Category.fun

    def test_invalid_category_rejected(self):
        with pytest.raises(ValidationError):
            Transaction(
                date=date(2025, 1, 15),
                amount=-10.0,
                merchant="X",
                category="invalid_category",
            )

    def test_all_categories_valid(self):
        for cat in Category:
            tx = TransactionCreate(
                date=date(2025, 1, 1),
                amount=1.0,
                merchant="Test",
                category=cat,
            )
            assert tx.category == cat

    def test_json_round_trip(self):
        tx = Transaction(
            date=date(2025, 3, 1),
            amount=-15.99,
            merchant="Spotify",
            category="bills",
            notes="Monthly sub",
        )
        data = tx.model_dump(mode="json")
        assert isinstance(data["id"], str)
        assert data["date"] == "2025-03-01"
        assert data["category"] == "bills"
        restored = Transaction.model_validate(data)
        assert restored.id == tx.id


class TestGoal:
    def test_create_goal(self):
        g = Goal(
            name="Emergency Fund",
            target_amount=10000.0,
            monthly_contribution=500.0,
            start_date=date(2025, 1, 1),
        )
        assert isinstance(g.id, UUID)
        assert g.name == "Emergency Fund"
        assert g.target_amount == 10000.0
        assert g.monthly_contribution == 500.0
        assert g.start_date == date(2025, 1, 1)

    def test_goal_json_round_trip(self):
        g = Goal(
            name="Vacation",
            target_amount=5000.0,
            monthly_contribution=200.0,
            start_date=date(2025, 6, 1),
        )
        data = g.model_dump(mode="json")
        assert data["start_date"] == "2025-06-01"
        restored = Goal.model_validate(data)
        assert restored.id == g.id

    def test_goal_create_no_id(self):
        gc = GoalCreate(
            name="Test",
            target_amount=100.0,
            monthly_contribution=10.0,
            start_date=date(2025, 1, 1),
        )
        assert not hasattr(gc, "id") or "id" not in gc.model_fields
