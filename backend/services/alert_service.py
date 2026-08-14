"""Price alert service for monitoring stock price movements."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


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


class AlertService:
    """Manage and trigger price alerts."""

    def __init__(self) -> None:
        """Initialize alert service."""
        # In-memory storage for MVP (would be database in production)
        self.alerts: dict[int, PriceAlert] = {}
        self.alert_id_counter = 1

    def create_alert(
        self,
        user_id: int,
        symbol: str,
        alert_type: AlertType,
        threshold: float,
    ) -> PriceAlert:
        """Create a new price alert.

        Args:
            user_id: User ID
            symbol: Stock symbol
            alert_type: Type of alert (price_above, price_below, etc.)
            threshold: Alert threshold value

        Returns:
            Created PriceAlert object
        """
        from datetime import datetime

        alert = PriceAlert(
            id=self.alert_id_counter,
            user_id=user_id,
            symbol=symbol,
            alert_type=alert_type,
            threshold=threshold,
            is_active=True,
            created_at=datetime.now().isoformat(),
        )
        self.alerts[self.alert_id_counter] = alert
        self.alert_id_counter += 1
        return alert

    def get_user_alerts(self, user_id: int) -> list[PriceAlert]:
        """Get all alerts for a user."""
        return [alert for alert in self.alerts.values() if alert.user_id == user_id]

    def check_alerts(self, symbol: str, current_price: float, change_pct: float, volume: str) -> list[PriceAlert]:
        """Check which alerts should be triggered for a symbol.

        Args:
            symbol: Stock symbol
            current_price: Current stock price
            change_pct: Percentage change
            volume: Trading volume

        Returns:
            List of triggered alerts
        """
        triggered = []

        for alert in self.alerts.values():
            if not alert.is_active or alert.symbol != symbol or alert.triggered_at:
                continue

            should_trigger = False

            if alert.alert_type == AlertType.PRICE_ABOVE:
                should_trigger = current_price > alert.threshold
            elif alert.alert_type == AlertType.PRICE_BELOW:
                should_trigger = current_price < alert.threshold
            elif alert.alert_type == AlertType.CHANGE_PERCENT:
                should_trigger = abs(change_pct) >= alert.threshold
            elif alert.alert_type == AlertType.VOLUME_SPIKE:
                # Simple volume check (would need historical data in production)
                volume_num = self._parse_volume(volume)
                should_trigger = volume_num > alert.threshold

            if should_trigger:
                alert.triggered_at = self._get_current_time()
                triggered.append(alert)

        return triggered

    def disable_alert(self, alert_id: int) -> bool:
        """Disable an alert."""
        if alert_id in self.alerts:
            self.alerts[alert_id].is_active = False
            return True
        return False

    def delete_alert(self, alert_id: int) -> bool:
        """Delete an alert."""
        if alert_id in self.alerts:
            del self.alerts[alert_id]
            return True
        return False

    def get_alert_summary(self, user_id: int) -> dict[str, object]:
        """Get summary of user's alerts."""
        user_alerts = self.get_user_alerts(user_id)
        active_alerts = [a for a in user_alerts if a.is_active]
        triggered_alerts = [a for a in user_alerts if a.triggered_at]

        return {
            "total_alerts": len(user_alerts),
            "active_alerts": len(active_alerts),
            "triggered_alerts": len(triggered_alerts),
            "alerts": user_alerts,
        }

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
        from datetime import datetime

        return datetime.now().isoformat()
