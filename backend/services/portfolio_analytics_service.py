"""Advanced portfolio analytics and performance metrics."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
import math


@dataclass
class PortfolioMetrics:
    """Portfolio performance and risk metrics."""

    total_value: float
    total_invested: float
    total_gain_loss: float
    total_return_pct: float
    xirr: float
    allocation: dict[str, float]
    sector_allocation: dict[str, float]
    top_performers: list[dict[str, object]]
    bottom_performers: list[dict[str, object]]
    volatility: float
    sharpe_ratio: float
    max_drawdown: float
    concentration_risk: float


class PortfolioAnalyticsService:
    """Calculate advanced portfolio metrics and analytics."""

    def __init__(self) -> None:
        """Initialize analytics service."""
        self.risk_free_rate = 0.06  # 6% annual risk-free rate

    def calculate_metrics(
        self, holdings: list[dict[str, object]], prices: dict[str, float]
    ) -> PortfolioMetrics:
        """Calculate comprehensive portfolio metrics.

        Args:
            holdings: List of portfolio holdings with qty, avg_price, current_price
            prices: Dict mapping symbols to current prices

        Returns:
            PortfolioMetrics object with all calculations
        """
        if not holdings:
            return self._empty_metrics()

        # Calculate basic values
        total_value = 0.0
        total_invested = 0.0
        gains = {}
        allocations = {}
        sector_allocations = {}

        for holding in holdings:
            symbol = holding.get("symbol", "")
            quantity = float(holding.get("quantity", 0))
            avg_price = float(holding.get("avg_price", 0))
            current_price = float(holding.get("current_price", 0))
            sector = holding.get("sector", "Other")

            invested = quantity * avg_price
            market_value = quantity * current_price
            gain_loss = market_value - invested

            total_invested += invested
            total_value += market_value
            gains[symbol] = {"gain_loss": gain_loss, "return_pct": (gain_loss / invested * 100) if invested > 0 else 0}
            allocations[symbol] = market_value
            sector_allocations[sector] = sector_allocations.get(sector, 0) + market_value

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

        # Calculate XIRR (simplified, using average daily return)
        xirr = self._calculate_xirr(total_return_pct)

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

        # Calculate risk metrics
        volatility = self._calculate_volatility(gains)
        sharpe_ratio = self._calculate_sharpe_ratio(total_return_pct, volatility)
        max_drawdown = self._calculate_max_drawdown(gains)
        concentration_risk = self._calculate_concentration_risk(allocation_pct)

        return PortfolioMetrics(
            total_value=round(total_value, 2),
            total_invested=round(total_invested, 2),
            total_gain_loss=round(total_gain_loss, 2),
            total_return_pct=round(total_return_pct, 2),
            xirr=round(xirr, 2),
            allocation=allocation_pct,
            sector_allocation=sector_allocation_pct,
            top_performers=top_performers,
            bottom_performers=bottom_performers,
            volatility=round(volatility, 2),
            sharpe_ratio=round(sharpe_ratio, 2),
            max_drawdown=round(max_drawdown, 2),
            concentration_risk=round(concentration_risk, 2),
        )

    def _calculate_xirr(self, total_return_pct: float) -> float:
        """Estimate XIRR based on total return.

        Simplified calculation assuming investment is held for ~1 year.
        """
        return total_return_pct / 100.0 * 100.0  # Return as percentage

    def _calculate_volatility(self, gains: dict[str, dict[str, float]]) -> float:
        """Calculate portfolio volatility from individual returns."""
        if not gains:
            return 0.0

        returns = [data["return_pct"] for data in gains.values()]
        mean_return = sum(returns) / len(returns)
        variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
        return math.sqrt(variance)

    def _calculate_sharpe_ratio(self, return_pct: float, volatility: float) -> float:
        """Calculate Sharpe ratio."""
        if volatility == 0:
            return 0.0
        return (return_pct - self.risk_free_rate) / volatility

    def _calculate_max_drawdown(self, gains: dict[str, dict[str, float]]) -> float:
        """Calculate maximum drawdown."""
        if not gains:
            return 0.0

        returns = [data["return_pct"] for data in gains.values()]
        if not returns:
            return 0.0

        running_max = returns[0]
        max_dd = 0.0

        for ret in returns:
            if ret > running_max:
                running_max = ret
            drawdown = running_max - ret
            if drawdown > max_dd:
                max_dd = drawdown

        return max_dd

    def _calculate_concentration_risk(self, allocations: dict[str, float]) -> float:
        """Calculate concentration risk using Herfindahl index."""
        if not allocations:
            return 0.0

        # Herfindahl index: sum of squared allocation percentages
        herfindahl = sum(alloc ** 2 for alloc in allocations.values())
        # Normalize to 0-100 scale (0 = perfectly diversified, 100 = fully concentrated)
        max_positions = len(allocations)
        min_herfindahl = 100 / max_positions  # Equally weighted
        normalized = ((herfindahl - min_herfindahl) / (10000 - min_herfindahl)) * 100
        return max(0, min(100, normalized))

    def _empty_metrics(self) -> PortfolioMetrics:
        """Return empty metrics object."""
        return PortfolioMetrics(
            total_value=0.0,
            total_invested=0.0,
            total_gain_loss=0.0,
            total_return_pct=0.0,
            xirr=0.0,
            allocation={},
            sector_allocation={},
            top_performers=[],
            bottom_performers=[],
            volatility=0.0,
            sharpe_ratio=0.0,
            max_drawdown=0.0,
            concentration_risk=0.0,
        )
