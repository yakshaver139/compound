from datetime import date

from app.models import Category, Transaction, Summary, compute_summary


def _tx(amount: float, category: Category = Category.other, d: date = date(2025, 1, 15)) -> Transaction:
    return Transaction(date=d, amount=amount, merchant="test", category=category)


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
