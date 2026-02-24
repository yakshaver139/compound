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
