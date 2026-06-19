"""Database models for IntelStock."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    chats = relationship("Chat", back_populates="user", cascade="all, delete-orphan")
    portfolio = relationship("Portfolio", back_populates="user", cascade="all, delete-orphan")
    watchlist = relationship("Watchlist", back_populates="user", cascade="all, delete-orphan")


class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    query = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    symbol = Column(String(50), nullable=True)
    recommendation = Column(String(255), nullable=True)
    confidence = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="chats")


class StockQuote(Base):
    __tablename__ = "stock_quotes"

    id = Column(Integer, primary_key=True)
    symbol = Column(String(50), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    price = Column(Float, nullable=False)
    change_pct = Column(Float, nullable=False)
    sentiment = Column(String(50), nullable=True)
    support = Column(Float, nullable=True)
    resistance = Column(Float, nullable=True)
    headline = Column(String(255), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class News(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True)
    symbol = Column(String(50), ForeignKey("stock_quotes.symbol"), nullable=False)
    headline = Column(String(255), nullable=False)
    source = Column(String(100), nullable=True)
    sentiment_score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Sentiment(Base):
    __tablename__ = "sentiments"

    id = Column(Integer, primary_key=True)
    symbol = Column(String(50), ForeignKey("stock_quotes.symbol"), nullable=False)
    label = Column(String(50), nullable=False)
    bullish_score = Column(Float, nullable=False)
    bearish_score = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Portfolio(Base):
    __tablename__ = "portfolios"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    symbol = Column(String(50), nullable=False)
    quantity = Column(Integer, nullable=False)
    average_cost = Column(Float, nullable=False)
    current_price = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="portfolio")


class Watchlist(Base):
    __tablename__ = "watchlists"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    symbol = Column(String(50), nullable=False)
    alert_price = Column(Float, nullable=True)
    alert_type = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="watchlist")


class Insight(Base):
    __tablename__ = "insights"

    id = Column(Integer, primary_key=True)
    symbol = Column(String(50), ForeignKey("stock_quotes.symbol"), nullable=False)
    summary = Column(Text, nullable=False)
    recommendation = Column(String(255), nullable=False)
    catalysts = Column(Text, nullable=True)
    risks = Column(Text, nullable=True)
    confidence = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
