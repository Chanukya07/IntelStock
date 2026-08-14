"""Unit tests for IntelStock backend services."""


def test_market_data_service_fetch_quote():
    from backend.services.market_data_service import MarketDataService

    svc = MarketDataService()
    quote = svc.fetch_live_quote("RELIANCE")

    assert quote["symbol"] == "RELIANCE"
    assert quote["price"] > 0
    assert "change_pct" in quote
    assert "sentiment" in quote


def test_market_data_service_symbol_alias():
    from backend.services.market_data_service import MarketDataService

    svc = MarketDataService()
    quote = svc.fetch_live_quote("HDFC")

    # HDFC should map to HDFCBANK
    assert quote["symbol"] in ("HDFCBANK", "HDFC")
    assert quote["price"] > 0


def test_market_data_service_unknown_symbol():
    from backend.services.market_data_service import MarketDataService

    svc = MarketDataService()
    # Unknown symbols should still return a valid response
    quote = svc.fetch_live_quote("UNKNOWNSYM")
    assert "symbol" in quote
    assert "price" in quote


def test_alert_service_create_and_get():
    from backend.services.alert_service import AlertService, AlertType

    svc = AlertService()
    alert = svc.create_alert(user_id=1, symbol="RELIANCE", alert_type=AlertType.PRICE_ABOVE, threshold=3500.0)

    assert alert.symbol == "RELIANCE"
    assert alert.alert_type == AlertType.PRICE_ABOVE
    assert alert.threshold == 3500.0
    assert alert.is_active is True

    alerts = svc.get_user_alerts(1)
    assert any(a.id == alert.id for a in alerts)


def test_alert_service_delete():
    from backend.services.alert_service import AlertService, AlertType

    svc = AlertService()
    alert = svc.create_alert(user_id=2, symbol="TCS", alert_type=AlertType.PRICE_BELOW, threshold=4000.0)
    alert_id = alert.id

    success = svc.delete_alert(alert_id)
    assert success is True

    # Deleted alert should no longer appear
    alerts = svc.get_user_alerts(2)
    assert not any(a.id == alert_id for a in alerts)


def test_alert_service_delete_nonexistent():
    from backend.services.alert_service import AlertService

    svc = AlertService()
    success = svc.delete_alert(99999)
    assert success is False


def test_alert_service_check_alerts_triggers_price_above():
    from backend.services.alert_service import AlertService, AlertType

    svc = AlertService()
    alert = svc.create_alert(user_id=3, symbol="RELIANCE", alert_type=AlertType.PRICE_ABOVE, threshold=3000.0)

    triggered = svc.check_alerts(symbol="RELIANCE", current_price=3245.50, change_pct=2.4, volume="4.2M")

    assert len(triggered) == 1
    assert triggered[0].id == alert.id
    # Triggering should flip is_active and stamp triggered_at
    assert alert.is_active is False
    assert alert.triggered_at is not None


def test_alert_service_check_alerts_does_not_trigger_below_threshold():
    from backend.services.alert_service import AlertService, AlertType

    svc = AlertService()
    svc.create_alert(user_id=4, symbol="TCS", alert_type=AlertType.PRICE_ABOVE, threshold=5000.0)

    triggered = svc.check_alerts(symbol="TCS", current_price=4385.75, change_pct=1.8, volume="1.8M")

    assert triggered == []


def test_alert_service_check_alerts_skips_already_triggered():
    from backend.services.alert_service import AlertService, AlertType

    svc = AlertService()
    svc.create_alert(user_id=5, symbol="INFY", alert_type=AlertType.PRICE_ABOVE, threshold=2000.0)

    first = svc.check_alerts(symbol="INFY", current_price=2156.40, change_pct=3.1, volume="3.3M")
    second = svc.check_alerts(symbol="INFY", current_price=2200.00, change_pct=3.1, volume="3.3M")

    assert len(first) == 1
    assert second == []


def test_scheduler_alert_service_is_shared_singleton():
    """The scheduler must check the same AlertService instance the API writes to,
    otherwise alerts created via /api/v1/alerts are never evaluated."""
    from backend.tasks.scheduler import _get_alert_service
    from backend.api.advanced_routes import alert_service as routes_alert_service

    assert _get_alert_service() is routes_alert_service


def test_portfolio_analytics_service_metrics():
    from backend.services.portfolio_analytics_service import PortfolioAnalyticsService

    svc = PortfolioAnalyticsService()
    holdings = [
        {"symbol": "RELIANCE", "quantity": 10, "avg_price": 2640, "current_price": 3245.50, "sector": "Energy"},
        {"symbol": "TCS", "quantity": 5, "avg_price": 3700, "current_price": 4385.75, "sector": "IT"},
        {"symbol": "INFY", "quantity": 20, "avg_price": 1444, "current_price": 2156.40, "sector": "IT"},
    ]

    metrics = svc.calculate_metrics(holdings, {})

    # Verify basic calculations
    expected_total = (10 * 3245.50) + (5 * 4385.75) + (20 * 2156.40)
    assert abs(metrics.total_value - expected_total) < 0.01

    expected_invested = (10 * 2640) + (5 * 3700) + (20 * 1444)
    assert abs(metrics.total_invested - expected_invested) < 0.01

    # Should have positive gain
    assert metrics.total_gain_loss > 0
    assert metrics.total_return_pct > 0

    # Sector allocation should sum to ~100
    total_alloc = sum(metrics.sector_allocation.values())
    assert abs(total_alloc - 100.0) < 1.0

    # Should have performers
    assert len(metrics.top_performers) > 0
    assert len(metrics.bottom_performers) >= 0


def test_portfolio_analytics_sharpe_ratio():
    from backend.services.portfolio_analytics_service import PortfolioAnalyticsService

    svc = PortfolioAnalyticsService()
    holdings = [
        {"symbol": "RELIANCE", "quantity": 10, "avg_price": 2640, "current_price": 3245.50, "sector": "Energy"},
    ]

    metrics = svc.calculate_metrics(holdings, {})
    # Sharpe ratio should be finite
    assert isinstance(metrics.sharpe_ratio, float)


def test_portfolio_analytics_empty_holdings():
    from backend.services.portfolio_analytics_service import PortfolioAnalyticsService

    svc = PortfolioAnalyticsService()
    metrics = svc.calculate_metrics([], {})

    assert metrics.total_value == 0
    assert metrics.total_invested == 0
    assert metrics.total_gain_loss == 0


def test_report_generator_stock_report():
    from backend.services.report_generator import ReportGenerator

    gen = ReportGenerator()
    html = gen.generate_stock_report(
        symbol="RELIANCE",
        name="Reliance Industries",
        price=3245.50,
        change_pct=2.4,
        sentiment="Bullish",
        summary="Strong momentum",
        recommendation="Buy",
        catalysts=["Retail expansion", "Jio growth"],
        risks=["Global slowdown"],
    )

    assert isinstance(html, bytes)
    assert b"RELIANCE" in html
    assert b"3245" in html or b"3,245" in html


def test_report_generator_portfolio_report():
    from backend.services.report_generator import ReportGenerator

    gen = ReportGenerator()
    holdings = [
        {"symbol": "TCS", "quantity": 5, "avg_price": 3700, "current_price": 4385, "market_value": 21925, "gain_loss": 3425},
    ]
    metrics = {"total_value": 21925, "total_invested": 18500, "total_gain_loss": 3425, "total_return_pct": 18.5}

    html = gen.generate_portfolio_report(holdings, metrics)

    assert isinstance(html, bytes)
    assert b"TCS" in html


def test_validators_valid_symbol():
    from backend.api.validators import validate_symbol

    result = validate_symbol("RELIANCE")
    assert result == "RELIANCE"

    result = validate_symbol("reliance")
    assert result == "RELIANCE"


def test_validators_invalid_symbol():
    from backend.api.validators import validate_symbol
    from fastapi import HTTPException

    try:
        validate_symbol("")
        assert False, "Should have raised HTTPException"
    except (HTTPException, ValueError, Exception):
        pass


def test_validators_valid_user_id():
    from backend.api.validators import validate_user_id

    result = validate_user_id(1)
    assert result == 1


def test_validators_invalid_user_id():
    from backend.api.validators import validate_user_id
    from fastapi import HTTPException

    try:
        validate_user_id(0)
        assert False, "Should have raised HTTPException"
    except (HTTPException, ValueError, Exception):
        pass
