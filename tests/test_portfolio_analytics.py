"""Tests for PortfolioAnalyticsService risk maths and honesty markers."""

import math

from backend.services.portfolio_analytics_service import (
    MIN_HISTORY_POINTS,
    STATUS_COMPUTED,
    STATUS_NO_CASH_FLOWS,
    STATUS_NO_HISTORY,
    TRADING_DAYS_PER_YEAR,
    PortfolioAnalyticsService,
)


def _holding(symbol, quantity=10, avg_price=100.0, current_price=100.0, sector="Other"):
    return {
        "symbol": symbol,
        "quantity": quantity,
        "avg_price": avg_price,
        "current_price": current_price,
        "sector": sector,
    }


def _equal_weight_holdings(n):
    """n holdings each worth exactly the same market value."""
    return [_holding(f"SYM{i}") for i in range(n)]


# --- Concentration risk (Herfindahl) ---------------------------------------


def test_equal_weight_portfolio_has_zero_concentration():
    svc = PortfolioAnalyticsService()

    for n in (2, 3, 10):
        metrics = svc.calculate_metrics(_equal_weight_holdings(n))
        assert metrics.concentration_risk == 0.0, f"n={n} should be perfectly diversified"


def test_single_holding_is_fully_concentrated():
    svc = PortfolioAnalyticsService()

    metrics = svc.calculate_metrics([_holding("RELIANCE")])

    assert metrics.concentration_risk == 100.0


def test_lopsided_portfolio_is_between_the_extremes():
    svc = PortfolioAnalyticsService()

    # 90 / 5 / 5 split by market value.
    holdings = [
        _holding("BIG", quantity=90),
        _holding("SMALL1", quantity=5),
        _holding("SMALL2", quantity=5),
    ]

    metrics = svc.calculate_metrics(holdings)

    # HHI = 90^2 + 5^2 + 5^2 = 8150; floor for 3 equal positions is 10000/3.
    expected = ((8150 - 10000 / 3) / (10000 - 10000 / 3)) * 100
    assert abs(metrics.concentration_risk - expected) < 0.01
    assert 0.0 < metrics.concentration_risk < 100.0


# --- Honesty markers --------------------------------------------------------


def test_risk_metrics_are_none_without_price_history():
    svc = PortfolioAnalyticsService()

    metrics = svc.calculate_metrics(_equal_weight_holdings(3))

    assert metrics.risk_metrics_available is False
    assert metrics.volatility is None
    assert metrics.sharpe_ratio is None
    assert metrics.max_drawdown is None
    assert metrics.xirr is None
    assert metrics.metric_status["volatility"] == STATUS_NO_HISTORY
    assert metrics.metric_status["sharpe_ratio"] == STATUS_NO_HISTORY
    assert metrics.metric_status["max_drawdown"] == STATUS_NO_HISTORY
    assert metrics.metric_status["xirr"] == STATUS_NO_CASH_FLOWS
    # The metrics that are genuinely derivable from a holdings snapshot stay real.
    assert metrics.metric_status["total_return_pct"] == STATUS_COMPUTED
    assert metrics.metric_status["concentration_risk"] == STATUS_COMPUTED


def test_empty_portfolio_flags_risk_metrics_unavailable():
    svc = PortfolioAnalyticsService()

    metrics = svc.calculate_metrics([])

    assert metrics.total_value == 0
    assert metrics.risk_metrics_available is False
    assert metrics.volatility is None
    assert metrics.sharpe_ratio is None
    assert metrics.max_drawdown is None
    assert metrics.xirr is None


def test_too_short_history_does_not_produce_a_number():
    svc = PortfolioAnalyticsService()

    history = {"RELIANCE": [100.0 + i for i in range(MIN_HISTORY_POINTS - 1)]}
    metrics = svc.calculate_metrics([_holding("RELIANCE")], {}, history)

    assert metrics.risk_metrics_available is False
    assert metrics.volatility is None


def test_partial_history_is_rejected_rather_than_marked_at_zero():
    """One missing symbol must not silently value that position at zero."""
    svc = PortfolioAnalyticsService()

    history = {"A": [100.0] * MIN_HISTORY_POINTS}
    metrics = svc.calculate_metrics([_holding("A"), _holding("B")], {}, history)

    assert metrics.risk_metrics_available is False
    assert metrics.max_drawdown is None


# --- Real risk maths when a price history is supplied -----------------------


def test_flat_history_gives_zero_volatility_and_no_sharpe():
    svc = PortfolioAnalyticsService()

    history = {"RELIANCE": [250.0] * (MIN_HISTORY_POINTS + 5)}
    metrics = svc.calculate_metrics([_holding("RELIANCE")], {}, history)

    assert metrics.risk_metrics_available is True
    assert metrics.volatility == 0.0
    assert metrics.max_drawdown == 0.0
    # Sharpe is undefined at zero volatility - it must not read as a real 0.00.
    assert metrics.sharpe_ratio is None


def test_volatility_matches_annualized_stdev_of_daily_returns():
    svc = PortfolioAnalyticsService()

    # Alternating +10% / -10% moves so the return series is exactly known.
    closes = [100.0]
    for i in range(MIN_HISTORY_POINTS + 10):
        closes.append(closes[-1] * (1.10 if i % 2 == 0 else 0.90))
    metrics = svc.calculate_metrics([_holding("X")], {}, {"X": closes})

    returns = [closes[i + 1] / closes[i] - 1 for i in range(len(closes) - 1)]
    mean = sum(returns) / len(returns)
    variance = sum((r - mean) ** 2 for r in returns) / (len(returns) - 1)
    expected = math.sqrt(variance) * math.sqrt(TRADING_DAYS_PER_YEAR) * 100

    assert metrics.volatility is not None
    assert abs(metrics.volatility - expected) < 0.01


def test_max_drawdown_is_the_peak_to_trough_of_the_equity_curve():
    svc = PortfolioAnalyticsService()

    # Rise to 200, fall to 150 (25% drawdown), recover to 210.
    closes = [100.0] * 10 + [200.0] * 5 + [150.0] * 5 + [210.0] * 5
    metrics = svc.calculate_metrics([_holding("X", quantity=3)], {}, {"X": closes})

    assert metrics.max_drawdown is not None
    assert abs(metrics.max_drawdown - 25.0) < 0.01


def test_max_drawdown_is_invariant_to_holdings_order():
    svc = PortfolioAnalyticsService()

    history = {
        "A": [100.0 + i for i in range(MIN_HISTORY_POINTS + 5)],
        "B": [50.0] * 10 + [80.0] * 5 + [40.0] * (MIN_HISTORY_POINTS - 10),
    }
    forward = svc.calculate_metrics([_holding("A"), _holding("B")], {}, history)
    reverse = svc.calculate_metrics([_holding("B"), _holding("A")], {}, history)

    assert forward.max_drawdown == reverse.max_drawdown
    assert forward.volatility == reverse.volatility


def test_sharpe_uses_a_consistent_percent_scale():
    svc = PortfolioAnalyticsService()

    closes = [100.0]
    for i in range(TRADING_DAYS_PER_YEAR):
        closes.append(closes[-1] * (1.01 if i % 2 == 0 else 0.995))
    metrics = svc.calculate_metrics([_holding("X")], {}, {"X": closes})

    periods = len(closes) - 1
    annualized_pct = ((closes[-1] / closes[0]) ** (TRADING_DAYS_PER_YEAR / periods) - 1) * 100
    expected = (annualized_pct - svc.risk_free_rate * 100) / metrics.volatility

    assert metrics.sharpe_ratio is not None
    assert abs(metrics.sharpe_ratio - expected) < 0.01


# --- Snapshot metrics that remain real --------------------------------------


def test_holding_return_dispersion_is_reported_separately():
    svc = PortfolioAnalyticsService()

    holdings = [
        _holding("UP", avg_price=100.0, current_price=120.0),
        _holding("DOWN", avg_price=100.0, current_price=80.0),
    ]
    metrics = svc.calculate_metrics(holdings)

    # Returns are +20% and -20%; population stdev is 20.
    assert abs(metrics.holding_return_dispersion_pct - 20.0) < 0.01
    # ...and it is not passed off as volatility.
    assert metrics.volatility is None


def test_prices_argument_overrides_holding_current_price():
    svc = PortfolioAnalyticsService()

    metrics = svc.calculate_metrics([_holding("RELIANCE", quantity=10, current_price=100.0)], {"RELIANCE": 150.0})

    assert metrics.total_value == 1500.0
    assert metrics.total_invested == 1000.0
    assert metrics.total_return_pct == 50.0
