"""Shared portfolio loading so every surface marks holdings to market the same way."""

from __future__ import annotations

from sqlalchemy.orm import Session

from backend.database import PortfolioRepository
from backend.services.market_data_service import MarketDataService

market_data_service = MarketDataService()


def build_user_holdings(
    db: Session, user_id: int, market_data: MarketDataService | None = None
) -> tuple[list[dict[str, object]], float, float]:
    """Load a user's holdings from the DB and mark them to market.

    Args:
        db: Database session
        user_id: User ID
        market_data: Optional market data service, so callers can reuse their own
            60s quote cache instead of warming a second one

    Returns:
        (holdings, total_value, total_invested) where each holding carries
        symbol, quantity, avg_price, current_price, market_value, gain_loss and sector
    """
    quotes = market_data or market_data_service

    holdings: list[dict[str, object]] = []
    total_value = 0.0
    total_invested = 0.0

    for holding in PortfolioRepository(db).get_user_portfolio(user_id):
        symbol = holding.stock.symbol
        # quantity/avg_price are Numeric (Decimal); cast so downstream float maths works.
        quantity = float(holding.quantity)
        avg_price = float(holding.avg_price)
        quote = quotes.fetch_live_quote(symbol)
        current_price = float(quote["price"])
        market_value = current_price * quantity

        total_value += market_value
        total_invested += avg_price * quantity

        holdings.append(
            {
                "id": holding.id,
                "symbol": symbol,
                "quantity": quantity,
                "avg_price": avg_price,
                "current_price": current_price,
                "market_value": round(market_value, 2),
                "gain_loss": round((current_price - avg_price) * quantity, 2),
                "sector": quote.get("sector", "Other"),
            }
        )

    return holdings, round(total_value, 2), round(total_invested, 2)
