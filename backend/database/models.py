"""Database models for IntelStock.

These SQLAlchemy models faithfully mirror ``backend/database/schema.sql``,
which is the canonical schema for the project. Table and column names are
kept in sync with that file so the ORM and the reference DDL never diverge.
"""

from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(255), unique=True, nullable=False)

    watchlists = relationship("Watchlist", back_populates="user", cascade="all, delete-orphan")
    portfolios = relationship("Portfolio", back_populates="user", cascade="all, delete-orphan")
    chats = relationship("ChatHistory", back_populates="user", cascade="all, delete-orphan")


class Stock(Base):
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True)
    symbol = Column(String(50), unique=True, nullable=False)
    company_name = Column(String(255), nullable=True)

    historical_prices = relationship("HistoricalPrice", back_populates="stock", cascade="all, delete-orphan")
    news = relationship("News", back_populates="stock", cascade="all, delete-orphan")
    insights = relationship("Insight", back_populates="stock", cascade="all, delete-orphan")


class HistoricalPrice(Base):
    __tablename__ = "historical_prices"

    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
    timestamp = Column(String(64), nullable=False)
    open = Column(Numeric, nullable=True)
    high = Column(Numeric, nullable=True)
    low = Column(Numeric, nullable=True)
    close = Column(Numeric, nullable=True)
    volume = Column(Numeric, nullable=True)

    stock = relationship("Stock", back_populates="historical_prices")


class News(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=True)
    title = Column(Text, nullable=False)
    source = Column(String(100), nullable=True)
    published_at = Column(String(64), nullable=True)
    content = Column(Text, nullable=True)

    stock = relationship("Stock", back_populates="news")
    sentiment_scores = relationship("SentimentScore", back_populates="news", cascade="all, delete-orphan")


class SentimentScore(Base):
    __tablename__ = "sentiment_scores"

    id = Column(Integer, primary_key=True)
    news_id = Column(Integer, ForeignKey("news.id"), nullable=False)
    bullish_score = Column(Numeric, nullable=True)
    bearish_score = Column(Numeric, nullable=True)
    analyzed_at = Column(String(64), nullable=True)

    news = relationship("News", back_populates="sentiment_scores")


class Watchlist(Base):
    __tablename__ = "watchlists"
    __table_args__ = (UniqueConstraint("user_id", "stock_id", name="uq_watchlist_user_stock"),)

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="watchlists")
    stock = relationship("Stock")


class Insight(Base):
    __tablename__ = "insights"

    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=True)
    recommendation = Column(Text, nullable=True)
    risk_summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    stock = relationship("Stock", back_populates="insights")


class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    prompt = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="chats")


class Portfolio(Base):
    __tablename__ = "portfolios"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    stock_id = Column(Integer, ForeignKey("stocks.id"), nullable=False)
    quantity = Column(Numeric, nullable=False)
    avg_price = Column(Numeric, nullable=False)

    user = relationship("User", back_populates="portfolios")
    stock = relationship("Stock")
