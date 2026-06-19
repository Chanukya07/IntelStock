"""Database module for IntelStock."""

from backend.database.models import (
    Base,
    User,
    Chat,
    StockQuote,
    News,
    Sentiment,
    Portfolio,
    Watchlist,
    Insight,
)
from backend.database.session import SessionLocal, get_db, init_db
from backend.database.repositories import (
    UserRepository,
    ChatRepository,
    StockQuoteRepository,
    NewsRepository,
    SentimentRepository,
    PortfolioRepository,
    WatchlistRepository,
    InsightRepository,
)

__all__ = [
    "Base",
    "User",
    "Chat",
    "StockQuote",
    "News",
    "Sentiment",
    "Portfolio",
    "Watchlist",
    "Insight",
    "SessionLocal",
    "get_db",
    "init_db",
    "UserRepository",
    "ChatRepository",
    "StockQuoteRepository",
    "NewsRepository",
    "SentimentRepository",
    "PortfolioRepository",
    "WatchlistRepository",
    "InsightRepository",
]
