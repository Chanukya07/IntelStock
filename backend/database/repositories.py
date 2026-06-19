"""Database repositories for data access."""

from datetime import datetime
from sqlalchemy.orm import Session

from backend.database.models import (
    User, Chat, StockQuote, News, Sentiment, Portfolio, Watchlist, Insight
)


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, username: str, email: str) -> User:
        user = User(username=username, email=email)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_by_id(self, user_id: int) -> User | None:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_username(self, username: str) -> User | None:
        return self.db.query(User).filter(User.username == username).first()


class ChatRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: int, query: str, response: str, symbol: str | None = None, recommendation: str | None = None, confidence: float | None = None) -> Chat:
        chat = Chat(user_id=user_id, query=query, response=response, symbol=symbol, recommendation=recommendation, confidence=confidence)
        self.db.add(chat)
        self.db.commit()
        self.db.refresh(chat)
        return chat

    def get_user_chats(self, user_id: int, limit: int = 50) -> list[Chat]:
        return self.db.query(Chat).filter(Chat.user_id == user_id).order_by(Chat.created_at.desc()).limit(limit).all()

    def get_by_symbol(self, symbol: str, limit: int = 10) -> list[Chat]:
        return self.db.query(Chat).filter(Chat.symbol == symbol).order_by(Chat.created_at.desc()).limit(limit).all()


class StockQuoteRepository:
    def __init__(self, db: Session):
        self.db = db

    def upsert(self, symbol: str, name: str, price: float, change_pct: float, sentiment: str | None = None, support: float | None = None, resistance: float | None = None, headline: str | None = None) -> StockQuote:
        quote = self.db.query(StockQuote).filter(StockQuote.symbol == symbol).first()
        if quote:
            quote.name = name
            quote.price = price
            quote.change_pct = change_pct
            quote.sentiment = sentiment
            quote.support = support
            quote.resistance = resistance
            quote.headline = headline
            quote.updated_at = datetime.utcnow()
        else:
            quote = StockQuote(symbol=symbol, name=name, price=price, change_pct=change_pct, sentiment=sentiment, support=support, resistance=resistance, headline=headline)
            self.db.add(quote)
        self.db.commit()
        self.db.refresh(quote)
        return quote

    def get(self, symbol: str) -> StockQuote | None:
        return self.db.query(StockQuote).filter(StockQuote.symbol == symbol).first()

    def get_all(self) -> list[StockQuote]:
        return self.db.query(StockQuote).all()


class NewsRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, symbol: str, headline: str, source: str | None = None, sentiment_score: float | None = None) -> News:
        news = News(symbol=symbol, headline=headline, source=source, sentiment_score=sentiment_score)
        self.db.add(news)
        self.db.commit()
        self.db.refresh(news)
        return news

    def get_by_symbol(self, symbol: str, limit: int = 20) -> list[News]:
        return self.db.query(News).filter(News.symbol == symbol).order_by(News.created_at.desc()).limit(limit).all()


class SentimentRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, symbol: str, label: str, bullish_score: float, bearish_score: float, confidence: float) -> Sentiment:
        sentiment = Sentiment(symbol=symbol, label=label, bullish_score=bullish_score, bearish_score=bearish_score, confidence=confidence)
        self.db.add(sentiment)
        self.db.commit()
        self.db.refresh(sentiment)
        return sentiment

    def get_latest(self, symbol: str) -> Sentiment | None:
        return self.db.query(Sentiment).filter(Sentiment.symbol == symbol).order_by(Sentiment.created_at.desc()).first()


class PortfolioRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: int, symbol: str, quantity: int, average_cost: float) -> Portfolio:
        portfolio = Portfolio(user_id=user_id, symbol=symbol, quantity=quantity, average_cost=average_cost)
        self.db.add(portfolio)
        self.db.commit()
        self.db.refresh(portfolio)
        return portfolio

    def get_user_portfolio(self, user_id: int) -> list[Portfolio]:
        return self.db.query(Portfolio).filter(Portfolio.user_id == user_id).all()

    def update_price(self, portfolio_id: int, current_price: float) -> Portfolio | None:
        portfolio = self.db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
        if portfolio:
            portfolio.current_price = current_price
            portfolio.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(portfolio)
        return portfolio


class WatchlistRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: int, symbol: str, alert_price: float | None = None, alert_type: str | None = None) -> Watchlist:
        watchlist = Watchlist(user_id=user_id, symbol=symbol, alert_price=alert_price, alert_type=alert_type)
        self.db.add(watchlist)
        self.db.commit()
        self.db.refresh(watchlist)
        return watchlist

    def get_user_watchlist(self, user_id: int) -> list[Watchlist]:
        return self.db.query(Watchlist).filter(Watchlist.user_id == user_id).all()

    def delete(self, watchlist_id: int) -> bool:
        result = self.db.query(Watchlist).filter(Watchlist.id == watchlist_id).delete()
        self.db.commit()
        return result > 0


class InsightRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, symbol: str, summary: str, recommendation: str, catalysts: str | None = None, risks: str | None = None, confidence: float = 0.5) -> Insight:
        insight = Insight(symbol=symbol, summary=summary, recommendation=recommendation, catalysts=catalysts, risks=risks, confidence=confidence)
        self.db.add(insight)
        self.db.commit()
        self.db.refresh(insight)
        return insight

    def get_latest(self, symbol: str) -> Insight | None:
        return self.db.query(Insight).filter(Insight.symbol == symbol).order_by(Insight.created_at.desc()).first()
