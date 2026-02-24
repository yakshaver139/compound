from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_home_returns_html():
    resp = client.get("/")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]


def test_home_contains_form():
    resp = client.get("/")
    html = resp.text
    assert "Add Transaction" in html
    assert '<form id="txn-form"' in html


def test_home_contains_transaction_list():
    resp = client.get("/")
    html = resp.text
    assert "Recent Transactions" in html
    assert 'id="txn-list"' in html


def test_home_contains_category_options():
    resp = client.get("/")
    html = resp.text
    for cat in ("groceries", "rent", "salary", "bills", "fun", "other"):
        assert f'value="{cat}"' in html


def test_home_links_to_summary():
    resp = client.get("/")
    assert '/summary-page' in resp.text


def test_summary_page_returns_html():
    resp = client.get("/summary-page")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]


def test_summary_page_contains_totals():
    resp = client.get("/summary-page")
    html = resp.text
    assert 'id="total-income"' in html
    assert 'id="total-expense"' in html
    assert 'id="total-net"' in html


def test_summary_page_contains_category_list():
    resp = client.get("/summary-page")
    html = resp.text
    assert "Spending by Category" in html
    assert 'id="category-list"' in html


def test_summary_page_links_to_transactions():
    resp = client.get("/summary-page")
    assert 'href="/"' in resp.text


def test_goals_page_returns_html():
    resp = client.get("/goals-page")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]


def test_goals_page_contains_form():
    resp = client.get("/goals-page")
    html = resp.text
    assert "Create Goal" in html
    assert '<form id="goal-form"' in html


def test_goals_page_contains_goal_list():
    resp = client.get("/goals-page")
    html = resp.text
    assert "Your Goals" in html
    assert 'id="goal-list"' in html


def test_goals_page_links_to_transactions():
    resp = client.get("/goals-page")
    assert 'href="/"' in resp.text


def test_goals_page_links_to_summary():
    resp = client.get("/goals-page")
    assert '/summary-page' in resp.text


def test_home_links_to_goals():
    resp = client.get("/")
    assert '/goals-page' in resp.text


def test_summary_page_links_to_goals():
    resp = client.get("/summary-page")
    assert '/goals-page' in resp.text
