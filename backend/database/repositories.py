"""Database repositories for data access.

All repositories operate on the normalized schema defined in
``backend/database/schema.sql`` (stocks referenced by ``stock_id``).
``StockRepository.get_or_create`` is the bridge between the symbol-based
service layer and the normalized storage layer.
"""

from datetime import datetime

from sqlalchemy.orm import Session

from backend.database.models import (
    Alert,
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


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_or_create(self, username: str) -> User:
        user = self.db.query(User).filter(User.username == username).first()
        if user is None:
            user = User(username=username)
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
        return user

    def get_by_id(self, user_id: int) -> User | None:
        return self.db.query(User).filter(User.id == user_id).first()

    def ensure_exists(self, user_id: int) -> User:
        """Ensure a row exists for an id-addressed user.

        The API identifies users by raw integer id, so rows carrying a
        ``users.id`` foreign key can be written for a user that was never
        inserted. The id is set explicitly rather than autoincremented so the
        caller's user_id stays valid.
        """
        user = self.get_by_id(user_id)
        if user is None:
            user = User(id=user_id, username=f"user{user_id}")
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
        return user


class StockRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_or_create(self, symbol: str, company_name: str | None = None) -> Stock:
        stock = self.db.query(Stock).filter(Stock.symbol == symbol).first()
        if stock is None:
            stock = Stock(symbol=symbol, company_name=company_name)
            self.db.add(stock)
            self.db.commit()
            self.db.refresh(stock)
        elif company_name and not stock.company_name:
            stock.company_name = company_name
            self.db.commit()
            self.db.refresh(stock)
        return stock

    def get_by_symbol(self, symbol: str) -> Stock | None:
        return self.db.query(Stock).filter(Stock.symbol == symbol).first()

    def get_all(self) -> list[Stock]:
        return self.db.query(Stock).all()


class HistoricalPriceRepository:
    def __init__(self, db: Session):
        self.db = db

    def add(self, stock_id: int, timestamp: str, open_: float, high: float, low: float, close: float, volume: float) -> HistoricalPrice:
        price = HistoricalPrice(
            stock_id=stock_id, timestamp=timestamp, open=open_, high=high, low=low, close=close, volume=volume
        )
        self.db.add(price)
        self.db.commit()
        self.db.refresh(price)
        return price

    def get_by_stock(self, stock_id: int, limit: int = 100) -> list[HistoricalPrice]:
        return (
            self.db.query(HistoricalPrice)
            .filter(HistoricalPrice.stock_id == stock_id)
            .order_by(HistoricalPrice.timestamp.desc())
            .limit(limit)
            .all()
        )


class NewsRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, stock_id: int | None, title: str, source: str | None = None, content: str | None = None, published_at: str | None = None) -> News:
        news = News(
            stock_id=stock_id,
            title=title,
            source=source,
            content=content,
            published_at=published_at or datetime.utcnow().isoformat(),
        )
        self.db.add(news)
        self.db.commit()
        self.db.refresh(news)
        return news

    def get_by_stock(self, stock_id: int, limit: int = 20) -> list[News]:
        return (
            self.db.query(News)
            .filter(News.stock_id == stock_id)
            .order_by(News.id.desc())
            .limit(limit)
            .all()
        )


class SentimentScoreRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, news_id: int, bullish_score: float, bearish_score: float) -> SentimentScore:
        score = SentimentScore(
            news_id=news_id,
            bullish_score=bullish_score,
            bearish_score=bearish_score,
            analyzed_at=datetime.utcnow().isoformat(),
        )
        self.db.add(score)
        self.db.commit()
        self.db.refresh(score)
        return score

    def get_for_news(self, news_id: int) -> SentimentScore | None:
        return (
            self.db.query(SentimentScore)
            .filter(SentimentScore.news_id == news_id)
            .order_by(SentimentScore.id.desc())
            .first()
        )


class WatchlistRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: int, stock_id: int) -> Watchlist:
        existing = (
            self.db.query(Watchlist)
            .filter(Watchlist.user_id == user_id, Watchlist.stock_id == stock_id)
            .first()
        )
        if existing:
            return existing
        watchlist = Watchlist(user_id=user_id, stock_id=stock_id)
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

    def create(self, stock_id: int | None, recommendation: str, risk_summary: str | None = None) -> Insight:
        insight = Insight(stock_id=stock_id, recommendation=recommendation, risk_summary=risk_summary)
        self.db.add(insight)
        self.db.commit()
        self.db.refresh(insight)
        return insight

    def get_latest(self, stock_id: int) -> Insight | None:
        return (
            self.db.query(Insight)
            .filter(Insight.stock_id == stock_id)
            .order_by(Insight.created_at.desc())
            .first()
        )


class ChatRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, prompt: str, response: str, user_id: int | None = None) -> ChatHistory:
        chat = ChatHistory(user_id=user_id, prompt=prompt, response=response)
        self.db.add(chat)
        self.db.commit()
        self.db.refresh(chat)
        return chat

    def get_user_chats(self, user_id: int, limit: int = 50) -> list[ChatHistory]:
        return (
            self.db.query(ChatHistory)
            .filter(ChatHistory.user_id == user_id)
            .order_by(ChatHistory.created_at.desc())
            .limit(limit)
            .all()
        )


class PortfolioRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: int, stock_id: int, quantity: float, avg_price: float) -> Portfolio:
        portfolio = Portfolio(user_id=user_id, stock_id=stock_id, quantity=quantity, avg_price=avg_price)
        self.db.add(portfolio)
        self.db.commit()
        self.db.refresh(portfolio)
        return portfolio

    def get_user_portfolio(self, user_id: int) -> list[Portfolio]:
        return self.db.query(Portfolio).filter(Portfolio.user_id == user_id).all()


class AlertRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: int, symbol: str, alert_type: str, threshold: float) -> Alert:
        alert = Alert(user_id=user_id, symbol=symbol, alert_type=alert_type, threshold=threshold, is_active=True)
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)
        return alert

    def get_by_id(self, alert_id: int) -> Alert | None:
        return self.db.query(Alert).filter(Alert.id == alert_id).first()

    def get_user_alerts(self, user_id: int) -> list[Alert]:
        return self.db.query(Alert).filter(Alert.user_id == user_id).order_by(Alert.id).all()

    def get_active(self, symbol: str | None = None) -> list[Alert]:
        """Alerts that are still armed: active and not yet triggered."""
        query = self.db.query(Alert).filter(Alert.is_active.is_(True), Alert.triggered_at.is_(None))
        if symbol is not None:
            query = query.filter(Alert.symbol == symbol)
        return query.order_by(Alert.id).all()

    def get_active_symbols(self) -> list[str]:
        """Distinct symbols that still have an armed alert."""
        rows = (
            self.db.query(Alert.symbol)
            .filter(Alert.is_active.is_(True), Alert.triggered_at.is_(None))
            .distinct()
            .all()
        )
        return [row[0] for row in rows]

    def mark_triggered(self, alert_id: int, triggered_price: float, triggered_at: datetime | None = None) -> Alert | None:
        alert = self.get_by_id(alert_id)
        if alert is None:
            return None
        alert.triggered_at = triggered_at or datetime.utcnow()
        alert.triggered_price = triggered_price
        alert.is_active = False
        self.db.commit()
        self.db.refresh(alert)
        return alert

    def set_active(self, alert_id: int, is_active: bool) -> bool:
        alert = self.get_by_id(alert_id)
        if alert is None:
            return False
        alert.is_active = is_active
        self.db.commit()
        return True

    def delete(self, alert_id: int, user_id: int | None = None) -> bool:
        query = self.db.query(Alert).filter(Alert.id == alert_id)
        if user_id is not None:
            # Ownership scoping: alert ids are durable now, so an unscoped
            # delete would let any user remove another user's alert.
            query = query.filter(Alert.user_id == user_id)
        result = query.delete()
        self.db.commit()
        return result > 0
