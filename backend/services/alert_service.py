"""Price alert service for monitoring stock price movements."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from sqlalchemy.orm import Session

from backend.database import Alert, AlertRepository, SessionLocal, UserRepository, init_db

# Tables are created by init_db() on app startup, but AlertService is also used
# outside the app (scheduler, tests), so the self-opened session path makes sure
# the schema exists once per process before touching it.
_schema_ready = False


class AlertType(Enum):
    """Types of price alerts."""

    PRICE_ABOVE = "price_above"
    PRICE_BELOW = "price_below"
    CHANGE_PERCENT = "change_percent"
    VOLUME_SPIKE = "volume_spike"


@dataclass
class PriceAlert:
    """Price alert configuration."""

    id: int
    user_id: int
    symbol: str
    alert_type: AlertType
    threshold: float
    is_active: bool
    created_at: str
    triggered_at: str | None = None
    triggered_price: float | None = None


class AlertService:
    """Manage and trigger price alerts, persisted in the ``alerts`` table."""

    def __init__(self, db: Session | None = None) -> None:
        """Initialize alert service.

        Args:
            db: Optional session used by every call that is not given one.
                When omitted the service opens (and closes) its own session
                per call, so a long-lived instance never holds an open one.
        """
        self._db = db
        # The dataclass handed out for a given alert id is reused, so a caller
        # holding a reference sees a later trigger reflected in place — the
        # behaviour of the previous in-memory implementation.
        self._alert_cache: dict[int, PriceAlert] = {}

    @contextmanager
    def _session(self, db: Session | None) -> Iterator[Session]:
        """Yield a usable session, opening a short-lived one only if needed."""
        session = db or self._db
        if session is not None:
            yield session
            return

        global _schema_ready
        if not _schema_ready:
            init_db()
            _schema_ready = True

        session = SessionLocal()
        try:
            yield session
        finally:
            session.close()

    def create_alert(
        self,
        user_id: int,
        symbol: str,
        alert_type: AlertType,
        threshold: float,
        db: Session | None = None,
    ) -> PriceAlert:
        """Create a new price alert.

        Args:
            user_id: User ID
            symbol: Stock symbol
            alert_type: Type of alert (price_above, price_below, etc.)
            threshold: Alert threshold value
            db: Optional session to use instead of opening one

        Returns:
            Created PriceAlert object
        """
        alert_type = AlertType(alert_type)

        with self._session(db) as session:
            # alerts.user_id is a real FK now, and the API addresses users by
            # raw id, so the row has to exist before the insert.
            UserRepository(session).ensure_exists(user_id)
            row = AlertRepository(session).create(
                user_id=user_id,
                symbol=symbol,
                alert_type=alert_type.value,
                threshold=threshold,
            )
            return self._to_dataclass(row)

    def get_user_alerts(self, user_id: int, db: Session | None = None) -> list[PriceAlert]:
        """Get all alerts for a user."""
        with self._session(db) as session:
            return [self._to_dataclass(row) for row in AlertRepository(session).get_user_alerts(user_id)]

    def check_alerts(
        self,
        symbol: str,
        current_price: float,
        change_pct: float,
        volume: str,
        db: Session | None = None,
    ) -> list[PriceAlert]:
        """Check which alerts should be triggered for a symbol.

        Args:
            symbol: Stock symbol
            current_price: Current stock price
            change_pct: Percentage change
            volume: Trading volume
            db: Optional session to use instead of opening one

        Returns:
            List of triggered alerts
        """
        triggered = []

        with self._session(db) as session:
            repo = AlertRepository(session)
            # Only armed alerts for this symbol — already-triggered rows are
            # excluded by the query, so an alert never fires twice.
            for row in repo.get_active(symbol=symbol):
                alert_type = AlertType(row.alert_type)
                threshold = float(row.threshold)
                should_trigger = False

                if alert_type == AlertType.PRICE_ABOVE:
                    should_trigger = current_price > threshold
                elif alert_type == AlertType.PRICE_BELOW:
                    should_trigger = current_price < threshold
                elif alert_type == AlertType.CHANGE_PERCENT:
                    should_trigger = abs(change_pct) >= threshold
                elif alert_type == AlertType.VOLUME_SPIKE:
                    # Simple volume check (would need historical data in production)
                    volume_num = self._parse_volume(volume)
                    should_trigger = volume_num > threshold

                if should_trigger:
                    updated = repo.mark_triggered(row.id, current_price)
                    triggered.append(self._to_dataclass(updated or row))

        return triggered

    def get_active_symbols(self, db: Session | None = None) -> list[str]:
        """Symbols that still have an armed alert, for the scheduler to poll."""
        with self._session(db) as session:
            return AlertRepository(session).get_active_symbols()

    def disable_alert(self, alert_id: int, db: Session | None = None) -> bool:
        """Disable an alert."""
        with self._session(db) as session:
            updated = AlertRepository(session).set_active(alert_id, False)
        if updated:
            cached = self._alert_cache.get(alert_id)
            if cached is not None:
                cached.is_active = False
        return updated

    def delete_alert(self, alert_id: int, user_id: int | None = None, db: Session | None = None) -> bool:
        """Delete an alert, optionally scoped to its owner."""
        with self._session(db) as session:
            deleted = AlertRepository(session).delete(alert_id, user_id=user_id)
        if deleted:
            self._alert_cache.pop(alert_id, None)
        return deleted

    def get_alert_summary(self, user_id: int, db: Session | None = None) -> dict[str, object]:
        """Get summary of user's alerts."""
        user_alerts = self.get_user_alerts(user_id, db=db)
        active_alerts = [a for a in user_alerts if a.is_active]
        triggered_alerts = [a for a in user_alerts if a.triggered_at]

        return {
            "total_alerts": len(user_alerts),
            "active_alerts": len(active_alerts),
            "triggered_alerts": len(triggered_alerts),
            "alerts": user_alerts,
        }

    def _to_dataclass(self, row: Alert) -> PriceAlert:
        """Map a DB row onto the PriceAlert shape callers already consume."""
        alert = self._alert_cache.get(row.id)
        if alert is None:
            alert = PriceAlert(
                id=row.id,
                user_id=row.user_id,
                symbol=row.symbol,
                alert_type=AlertType(row.alert_type),
                threshold=float(row.threshold),
                is_active=bool(row.is_active),
                created_at=self._isoformat(row.created_at) or "",
            )
            self._alert_cache[row.id] = alert
        else:
            alert.user_id = row.user_id
            alert.symbol = row.symbol
            alert.alert_type = AlertType(row.alert_type)
            alert.threshold = float(row.threshold)
            alert.is_active = bool(row.is_active)
            alert.created_at = self._isoformat(row.created_at) or ""

        alert.triggered_at = self._isoformat(row.triggered_at)
        alert.triggered_price = float(row.triggered_price) if row.triggered_price is not None else None
        return alert

    @staticmethod
    def _isoformat(value: datetime | str | None) -> str | None:
        """Render a timestamp column as the ISO string PriceAlert exposes."""
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.isoformat()
        return str(value)

    @staticmethod
    def _parse_volume(volume: str) -> float:
        """Parse volume string like '4.2M' to number."""
        volume = volume.upper().strip()
        if volume.endswith("M"):
            return float(volume[:-1]) * 1_000_000
        elif volume.endswith("K"):
            return float(volume[:-1]) * 1_000
        else:
            try:
                return float(volume)
            except ValueError:
                return 0.0

    @staticmethod
    def _get_current_time() -> str:
        """Get current ISO timestamp."""
        return datetime.now().isoformat()
