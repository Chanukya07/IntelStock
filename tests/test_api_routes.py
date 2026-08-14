"""Integration tests for FastAPI API routes using TestClient."""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    """Create test client with app."""
    from backend.main import app
    with TestClient(app) as c:
        yield c


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


def test_get_stock_valid(client):
    response = client.get("/stock", params={"symbol": "RELIANCE"})
    assert response.status_code == 200
    data = response.json()
    assert "symbol" in data
    assert "price" in data
    assert data["price"] > 0


def test_get_stock_lowercase(client):
    response = client.get("/stock", params={"symbol": "tcs"})
    assert response.status_code == 200
    data = response.json()
    assert data["symbol"] == "TCS"


def test_get_news(client):
    response = client.get("/news", params={"symbol": "RELIANCE"})
    assert response.status_code == 200
    data = response.json()
    assert "news" in data or isinstance(data, list) or "symbol" in data


def test_get_sentiment(client):
    response = client.get("/sentiment", params={"symbol": "TCS"})
    assert response.status_code == 200
    data = response.json()
    assert "sentiment" in data or "symbol" in data


def test_get_insights(client):
    response = client.get("/insights", params={"symbol": "INFY"})
    assert response.status_code == 200


def test_get_portfolio(client):
    response = client.get("/portfolio", params={"user_id": 1})
    assert response.status_code == 200


def test_get_watchlist(client):
    response = client.get("/watchlist", params={"user_id": 1})
    assert response.status_code == 200


def test_advanced_get_alerts(client):
    response = client.get("/api/v1/alerts", params={"user_id": 1})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "alerts" in data


def test_advanced_create_alert(client):
    response = client.post(
        "/api/v1/alerts",
        json={"symbol": "RELIANCE", "alert_type": "price_above", "threshold": 3500.0},
        params={"user_id": 1},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "alert_id" in data


def test_advanced_portfolio_analytics(client):
    response = client.get("/api/v1/portfolio/analytics", params={"user_id": 1})
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "metrics" in data
    metrics = data["metrics"]
    assert "total_value" in metrics
    assert "sharpe_ratio" in metrics
    assert "volatility" in metrics


def test_advanced_stock_report(client):
    response = client.get("/api/v1/reports/stock", params={"symbol": "TCS"})
    assert response.status_code == 200
    assert b"TCS" in response.content


def test_advanced_portfolio_report(client):
    response = client.get("/api/v1/reports/portfolio", params={"user_id": 1})
    assert response.status_code == 200
    assert len(response.content) > 100


def test_advanced_sentiment_report(client):
    response = client.get("/api/v1/reports/sentiment")
    assert response.status_code == 200
    assert len(response.content) > 100
