"""Database module for IntelStock."""

from backend.database.models import (
    Base,
    ChatHistory,
    HistoricalPrice,
    Insight,
    News,
    Portfolio,
    SentimentScore,
    Stock,
    User,
    Watchlist,
)
from backend.database.repositories import (
    ChatRepository,
    HistoricalPriceRepository,
    InsightRepository,
    NewsRepository,
    PortfolioRepository,
    SentimentScoreRepository,
    StockRepository,
    UserRepository,
    WatchlistRepository,
)
from backend.database.session import SessionLocal, get_db, init_db

__all__ = [
    "Base",
    "User",
    "Stock",
    "HistoricalPrice",
    "News",
    "SentimentScore",
    "Watchlist",
    "Insight",
    "ChatHistory",
    "Portfolio",
    "SessionLocal",
    "get_db",
    "init_db",
    "UserRepository",
    "StockRepository",
    "HistoricalPriceRepository",
    "NewsRepository",
    "SentimentScoreRepository",
    "WatchlistRepository",
    "InsightRepository",
    "ChatRepository",
    "PortfolioRepository",
]
