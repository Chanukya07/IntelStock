"""Advanced portfolio analytics and performance metrics.

Risk metrics (volatility, Sharpe, max drawdown) are time-series quantities: they
cannot be derived from a snapshot of holdings. When no price history is supplied
they are reported as ``None`` and flagged via ``risk_metrics_available`` /
``metric_status`` rather than filled with a plausible-looking placeholder.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import math

# Annualisation factor for daily returns on Indian equity markets.
TRADING_DAYS_PER_YEAR = 252

# Shortest price series we are willing to annualise. Below this the estimate is
# dominated by noise, so we report "unavailable" instead of a confident number.
MIN_HISTORY_POINTS = 20

STATUS_COMPUTED = "computed"
STATUS_NO_HISTORY = "unavailable: requires price history"
STATUS_NO_CASH_FLOWS = "unavailable: requires dated cash flows (holdings carry no purchase date)"
STATUS_NO_VOLATILITY = "unavailable: volatility is zero"
STATUS_CROSS_SECTIONAL = "computed: dispersion across holdings, not a time series"


@dataclass
class PortfolioMetrics:
    """Portfolio performance and risk metrics.

    ``xirr``, ``volatility``, ``sharpe_ratio`` and ``max_drawdown`` are ``None``
    whenever the inputs needed to compute them honestly are missing. Consumers
    must check for ``None`` (or read ``risk_metrics_available``) before
    formatting them as numbers.
    """

    total_value: float
    total_invested: float
    total_gain_loss: float
    total_return_pct: float
    xirr: float | None
    allocation: dict[str, float]
    sector_allocation: dict[str, float]
    top_performers: list[dict[str, object]]
    bottom_performers: list[dict[str, object]]
    volatility: float | None
    sharpe_ratio: float | None
    max_drawdown: float | None
    concentration_risk: float
    # True only when volatility/Sharpe/drawdown were computed from a real
    # portfolio equity curve. False means the risk tiles have no data behind them.
    risk_metrics_available: bool = False
    # Cross-sectional standard deviation of the individual holdings' returns.
    # This is a real, well-defined number - it is simply not annualised
    # volatility, which is why it has its own field.
    holding_return_dispersion_pct: float = 0.0
    # Per-metric provenance so a caller can tell a measurement from a gap.
    metric_status: dict[str, str] = field(default_factory=dict)


class PortfolioAnalyticsService:
    """Calculate advanced portfolio metrics and analytics."""

    def __init__(self) -> None:
        """Initialize analytics service."""
        self.risk_free_rate = 0.06  # 6% annual risk-free rate, as a fraction

    def calculate_metrics(
        self,
        holdings: list[dict[str, object]],
        prices: dict[str, float] | None = None,
        price_history: dict[str, list[float]] | None = None,
    ) -> PortfolioMetrics:
        """Calculate comprehensive portfolio metrics.

        Args:
            holdings: List of portfolio holdings with quantity, avg_price, current_price
            prices: Optional symbol -> price overrides for the marked-to-market value
            price_history: Optional symbol -> chronological close prices. Without it
                the time-series risk metrics are reported as unavailable rather
                than estimated.

        Returns:
            PortfolioMetrics object with all calculations
        """
        if not holdings:
            return self._empty_metrics()

        prices = prices or {}

        # Calculate basic values
        total_value = 0.0
        total_invested = 0.0
        gains = {}
        allocations = {}
        sector_allocations = {}
        quantities: dict[str, float] = {}

        for holding in holdings:
            symbol = holding.get("symbol", "")
            quantity = float(holding.get("quantity", 0))
            avg_price = float(holding.get("avg_price", 0))
            current_price = float(prices.get(symbol, holding.get("current_price", 0)))
            sector = holding.get("sector", "Other")

            invested = quantity * avg_price
            market_value = quantity * current_price
            gain_loss = market_value - invested

            total_invested += invested
            total_value += market_value
            gains[symbol] = {"gain_loss": gain_loss, "return_pct": (gain_loss / invested * 100) if invested > 0 else 0}
            allocations[symbol] = market_value
            sector_allocations[sector] = sector_allocations.get(sector, 0) + market_value
            quantities[symbol] = quantities.get(symbol, 0.0) + quantity

        # Normalize allocations to percentages
        allocation_pct = {
            sym: (val / total_value * 100) if total_value > 0 else 0
            for sym, val in allocations.items()
        }
        sector_allocation_pct = {
            sector: (val / total_value * 100) if total_value > 0 else 0
            for sector, val in sector_allocations.items()
        }

        # Calculate returns
        total_gain_loss = total_value - total_invested
        total_return_pct = (total_gain_loss / total_invested * 100) if total_invested > 0 else 0

        # Identify top and bottom performers
        sorted_gains = sorted(
            [(sym, data["return_pct"]) for sym, data in gains.items()],
            key=lambda x: x[1],
            reverse=True,
        )
        top_performers = [
            {"symbol": sym, "return_pct": ret} for sym, ret in sorted_gains[:3]
        ]
        bottom_performers = [
            {"symbol": sym, "return_pct": ret} for sym, ret in sorted_gains[-3:]
        ]

        # Risk metrics: only real if we were handed a price history to build an
        # equity curve from. Otherwise they stay None and are flagged as such.
        curve = self._build_equity_curve(quantities, price_history)
        volatility = self._calculate_volatility(curve)
        max_drawdown = self._calculate_max_drawdown(curve)
        sharpe_ratio = self._calculate_sharpe_ratio(curve, volatility)
        dispersion = self._calculate_return_dispersion(gains)
        concentration_risk = self._calculate_concentration_risk(allocation_pct)

        metric_status = {
            "total_return_pct": STATUS_COMPUTED,
            "concentration_risk": STATUS_COMPUTED,
            "holding_return_dispersion_pct": STATUS_CROSS_SECTIONAL,
            # No holding carries a purchase date anywhere in the schema, so there
            # are no dated cash flows to solve an internal rate of return over.
            "xirr": STATUS_NO_CASH_FLOWS,
            "volatility": STATUS_COMPUTED if volatility is not None else STATUS_NO_HISTORY,
            "max_drawdown": STATUS_COMPUTED if max_drawdown is not None else STATUS_NO_HISTORY,
            "sharpe_ratio": (
                STATUS_COMPUTED
                if sharpe_ratio is not None
                else (STATUS_NO_VOLATILITY if volatility is not None else STATUS_NO_HISTORY)
            ),
        }

        return PortfolioMetrics(
            total_value=round(total_value, 2),
            total_invested=round(total_invested, 2),
            total_gain_loss=round(total_gain_loss, 2),
            total_return_pct=round(total_return_pct, 2),
            xirr=None,
            allocation=allocation_pct,
            sector_allocation=sector_allocation_pct,
            top_performers=top_performers,
            bottom_performers=bottom_performers,
            volatility=self._round_optional(volatility),
            sharpe_ratio=self._round_optional(sharpe_ratio),
            max_drawdown=self._round_optional(max_drawdown),
            concentration_risk=round(concentration_risk, 2),
            risk_metrics_available=volatility is not None,
            holding_return_dispersion_pct=round(dispersion, 2),
            metric_status=metric_status,
        )

    @staticmethod
    def _round_optional(value: float | None) -> float | None:
        """Round a metric that may legitimately be unavailable."""
        return None if value is None else round(value, 2)

    def _build_equity_curve(
        self,
        quantities: dict[str, float],
        price_history: dict[str, list[float]] | None,
    ) -> list[float] | None:
        """Build the portfolio's value curve from per-symbol close prices.

        Returns None unless every held symbol has at least MIN_HISTORY_POINTS
        observations - a partial curve would silently mark missing positions at
        zero and manufacture a drawdown that never happened.
        """
        if not price_history or not quantities:
            return None

        series = {}
        for symbol, quantity in quantities.items():
            closes = price_history.get(symbol)
            if not closes or len(closes) < MIN_HISTORY_POINTS:
                return None
            series[symbol] = (quantity, closes)

        # Symbols can have differing history lengths (recent listings); align on
        # the most recent overlapping window.
        window = min(len(closes) for _, closes in series.values())
        curve = []
        for i in range(window):
            total = 0.0
            for quantity, closes in series.values():
                total += quantity * float(closes[len(closes) - window + i])
            curve.append(total)
        return curve

    @staticmethod
    def _daily_returns(curve: list[float] | None) -> list[float]:
        """Simple period-over-period returns of an equity curve."""
        if not curve:
            return []
        returns = []
        for prev, cur in zip(curve, curve[1:]):
            if prev > 0:
                returns.append(cur / prev - 1)
        return returns

    def _calculate_volatility(self, curve: list[float] | None) -> float | None:
        """Annualised standard deviation of portfolio returns, in percent."""
        returns = self._daily_returns(curve)
        if len(returns) < 2:
            return None

        mean_return = sum(returns) / len(returns)
        # Sample variance: the series is a sample of the return process.
        variance = sum((r - mean_return) ** 2 for r in returns) / (len(returns) - 1)
        return math.sqrt(variance) * math.sqrt(TRADING_DAYS_PER_YEAR) * 100

    def _calculate_sharpe_ratio(
        self, curve: list[float] | None, volatility: float | None
    ) -> float | None:
        """Sharpe ratio from the annualised return and volatility of the curve.

        Both operands are on the percent scale; the previous implementation
        compared a percentage against a 0.06 fraction.
        """
        if not curve or volatility is None or volatility == 0:
            return None
        if curve[0] <= 0:
            return None

        periods = len(curve) - 1
        growth = curve[-1] / curve[0]
        if growth <= 0:
            return None
        annualized_return_pct = (growth ** (TRADING_DAYS_PER_YEAR / periods) - 1) * 100
        return (annualized_return_pct - self.risk_free_rate * 100) / volatility

    def _calculate_max_drawdown(self, curve: list[float] | None) -> float | None:
        """Worst peak-to-trough decline of the equity curve, as a positive percent."""
        if not curve or len(curve) < 2:
            return None

        running_max = curve[0]
        max_dd = 0.0
        for value in curve:
            if value > running_max:
                running_max = value
            if running_max > 0:
                drawdown = (running_max - value) / running_max * 100
                if drawdown > max_dd:
                    max_dd = drawdown
        return max_dd

    @staticmethod
    def _calculate_return_dispersion(gains: dict[str, dict[str, float]]) -> float:
        """Spread of returns across holdings (cross-sectional, not volatility)."""
        if not gains:
            return 0.0

        returns = [data["return_pct"] for data in gains.values()]
        mean_return = sum(returns) / len(returns)
        variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
        return math.sqrt(variance)

    def _calculate_concentration_risk(self, allocations: dict[str, float]) -> float:
        """Calculate concentration risk using a normalized Herfindahl index."""
        if not allocations:
            return 0.0

        # Herfindahl index: sum of squared allocation percentages, so a single
        # 100% holding scores 100^2 = 10000 and N equal holdings score 10000/N.
        herfindahl = sum(alloc ** 2 for alloc in allocations.values())
        max_positions = len(allocations)
        if max_positions == 1:
            return 100.0

        # Equal-weight floor lives on the percentage-squared scale (10000/N), not
        # 100/N - using 100/N made a perfectly diversified 3-stock book read 33%.
        min_herfindahl = 10000 / max_positions
        normalized = ((herfindahl - min_herfindahl) / (10000 - min_herfindahl)) * 100
        # Clamp: floating-point noise can push an equal-weighted book slightly negative.
        return max(0.0, min(100.0, normalized))

    def _empty_metrics(self) -> PortfolioMetrics:
        """Return empty metrics object."""
        return PortfolioMetrics(
            total_value=0.0,
            total_invested=0.0,
            total_gain_loss=0.0,
            total_return_pct=0.0,
            xirr=None,
            allocation={},
            sector_allocation={},
            top_performers=[],
            bottom_performers=[],
            volatility=None,
            sharpe_ratio=None,
            max_drawdown=None,
            concentration_risk=0.0,
            risk_metrics_available=False,
            holding_return_dispersion_pct=0.0,
            metric_status={
                "total_return_pct": STATUS_COMPUTED,
                "concentration_risk": STATUS_COMPUTED,
                "holding_return_dispersion_pct": STATUS_CROSS_SECTIONAL,
                "xirr": STATUS_NO_CASH_FLOWS,
                "volatility": STATUS_NO_HISTORY,
                "max_drawdown": STATUS_NO_HISTORY,
                "sharpe_ratio": STATUS_NO_HISTORY,
            },
        )
