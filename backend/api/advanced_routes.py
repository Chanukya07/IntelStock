"""Advanced API routes for alerts, reports, and analytics."""

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.api.validators import validate_symbol, validate_user_id
from backend.database import get_db
from backend.services.alert_service import AlertService, AlertType
from backend.services.portfolio_analytics_service import PortfolioAnalyticsService
from backend.services.report_generator import ReportGenerator
from backend.services.market_data_service import MarketDataService

router = APIRouter(prefix="/api/v1", tags=["advanced"])

alert_service = AlertService()
analytics_service = PortfolioAnalyticsService()
report_generator = ReportGenerator()
market_data_service = MarketDataService()


class AlertRequest(BaseModel):
    """Price alert creation request."""

    symbol: str
    alert_type: str
    threshold: float


class AlertResponse(BaseModel):
    """Alert response model."""

    id: int
    symbol: str
    alert_type: str
    threshold: float
    is_active: bool


@router.post("/alerts")
def create_alert(user_id: int, payload: AlertRequest) -> dict[str, object]:
    """Create a new price alert.

    Args:
        user_id: User ID
        payload: Alert configuration

    Returns:
        Created alert details
    """
    user_id = validate_user_id(user_id)
    symbol = validate_symbol(payload.symbol)

    alert_type = AlertType(payload.alert_type)
    alert = alert_service.create_alert(user_id, symbol, alert_type, payload.threshold)

    return {
        "status": "ok",
        "alert_id": alert.id,
        "symbol": alert.symbol,
        "alert_type": alert.alert_type.value,
        "threshold": alert.threshold,
    }


@router.get("/alerts")
def get_alerts(user_id: int) -> dict[str, object]:
    """Get all alerts for a user."""
    user_id = validate_user_id(user_id)
    alerts = alert_service.get_user_alerts(user_id)

    return {
        "status": "ok",
        "user_id": user_id,
        "alerts": [
            {
                "id": a.id,
                "symbol": a.symbol,
                "alert_type": a.alert_type.value,
                "threshold": a.threshold,
                "is_active": a.is_active,
                "triggered_at": a.triggered_at,
            }
            for a in alerts
        ],
    }


@router.delete("/alerts/{alert_id}")
def delete_alert(alert_id: int) -> dict[str, str]:
    """Delete an alert."""
    success = alert_service.delete_alert(alert_id)
    return {"status": "ok" if success else "error", "message": "Alert deleted" if success else "Alert not found"}


@router.get("/portfolio/analytics")
def get_portfolio_analytics(user_id: int, db: Session = Depends(get_db)) -> dict[str, object]:
    """Get advanced portfolio analytics."""
    user_id = validate_user_id(user_id)

    # Fetch portfolio holdings (mock for now)
    holdings = [
        {
            "symbol": "RELIANCE",
            "quantity": 10,
            "avg_price": 2640,
            "current_price": 2987,
            "sector": "Energy",
        },
        {
            "symbol": "TCS",
            "quantity": 5,
            "avg_price": 3700,
            "current_price": 4124,
            "sector": "IT",
        },
        {
            "symbol": "INFY",
            "quantity": 20,
            "avg_price": 1444,
            "current_price": 1925,
            "sector": "IT",
        },
    ]

    metrics = analytics_service.calculate_metrics(holdings, {})

    return {
        "status": "ok",
        "user_id": user_id,
        "total_value": metrics.total_value,
        "total_invested": metrics.total_invested,
        "total_gain_loss": metrics.total_gain_loss,
        "total_return_pct": metrics.total_return_pct,
        "xirr": metrics.xirr,
        "volatility": metrics.volatility,
        "sharpe_ratio": metrics.sharpe_ratio,
        "max_drawdown": metrics.max_drawdown,
        "concentration_risk": metrics.concentration_risk,
        "allocation": metrics.allocation,
        "sector_allocation": metrics.sector_allocation,
        "top_performers": metrics.top_performers,
        "bottom_performers": metrics.bottom_performers,
    }


@router.get("/reports/stock")
def generate_stock_report(symbol: str) -> StreamingResponse:
    """Generate stock research report as PDF/HTML."""
    symbol = validate_symbol(symbol)

    quote = market_data_service.fetch_live_quote(symbol)

    # Mock insight data
    html_bytes = report_generator.generate_stock_report(
        symbol=quote["symbol"],
        name=quote["name"],
        price=quote["price"],
        change_pct=quote["change_pct"],
        sentiment=quote["sentiment"],
        summary=f"{quote['name']} shows bullish momentum with strong price action.",
        recommendation="Buy on dips below support level.",
        catalysts=["Strong earnings growth", "Positive sector momentum"],
        risks=["Market volatility", "Macroeconomic headwinds"],
    )

    return StreamingResponse(
        iter([html_bytes]),
        media_type="text/html",
        headers={"Content-Disposition": f"attachment; filename={symbol}_report.html"},
    )


@router.get("/reports/portfolio")
def generate_portfolio_report(user_id: int) -> StreamingResponse:
    """Generate portfolio statement report as PDF/HTML."""
    user_id = validate_user_id(user_id)

    holdings = [
        {
            "symbol": "RELIANCE",
            "quantity": 10,
            "avg_price": 2640,
            "current_price": 2987,
            "market_value": 29870,
            "gain_loss": 3470,
        },
        {
            "symbol": "TCS",
            "quantity": 5,
            "avg_price": 3700,
            "current_price": 4124,
            "market_value": 20620,
            "gain_loss": 2120,
        },
    ]

    metrics = {
        "total_value": 50490.0,
        "total_invested": 44900.0,
        "total_gain_loss": 5590.0,
        "total_return_pct": 12.45,
    }

    html_bytes = report_generator.generate_portfolio_report(holdings, metrics)

    return StreamingResponse(
        iter([html_bytes]),
        media_type="text/html",
        headers={"Content-Disposition": f"attachment; filename=portfolio_report_{user_id}.html"},
    )


@router.get("/reports/sentiment")
def generate_sentiment_report() -> StreamingResponse:
    """Generate market sentiment report as PDF/HTML."""
    stocks = [
        {"symbol": "RELIANCE", "name": "Reliance Industries", "sentiment": "Bullish", "confidence": 0.85},
        {"symbol": "TCS", "name": "Tata Consultancy", "sentiment": "Bullish", "confidence": 0.78},
        {"symbol": "HDFC", "name": "HDFC Bank", "sentiment": "Neutral", "confidence": 0.65},
        {"symbol": "INFY", "name": "Infosys", "sentiment": "Bullish", "confidence": 0.82},
    ]

    html_bytes = report_generator.generate_sentiment_report(stocks)

    return StreamingResponse(
        iter([html_bytes]),
        media_type="text/html",
        headers={"Content-Disposition": "attachment; filename=sentiment_report.html"},
    )
