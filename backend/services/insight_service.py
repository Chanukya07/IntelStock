"""Insight service for AI investment reports."""

from __future__ import annotations

from backend.services.market_data_service import MarketDataService
from backend.services.news_intelligence_service import NewsIntelligenceService
from backend.services.sentiment_service import SentimentService


class InsightService:
    def __init__(self) -> None:
        self.market_data_service = MarketDataService()
        self.news_service = NewsIntelligenceService()
        self.sentiment_service = SentimentService()

    def generate_report(self, symbol: str, query: str | None = None) -> dict[str, object]:
        quote = self.market_data_service.fetch_live_quote(symbol)
        news = self.news_service.fetch_company_news(symbol)
        news_text = " ".join(news["headlines"]) if isinstance(news.get("headlines"), list) else ""
        sentiment = self.sentiment_service.score_news(news_text)

        change_pct = float(quote["change_pct"])
        trend_bias = "Bullish" if change_pct > 0.75 else "Bearish" if change_pct < -0.75 else "Neutral"
        if sentiment["label"] == "Bullish":
            recommendation = "Accumulate on dips"
        elif sentiment["label"] == "Bearish":
            recommendation = "Trim exposure and wait for confirmation"
        else:
            recommendation = "Hold and watch for a breakout"

        if query:
            lowered = query.lower()
            if "short" in lowered or "intraday" in lowered:
                recommendation = f"{recommendation} with a tight risk budget"
            elif "long" in lowered or "portfolio" in lowered:
                recommendation = f"{recommendation} for a multi-quarter horizon"

        summary = (
            f"{quote['name']} is showing {trend_bias.lower()} momentum with price at ₹{quote['price']:,}. "
            f"Sentiment reads {sentiment['label'].lower()} and the nearest levels sit around "
            f"₹{quote['support']:,} / ₹{quote['resistance']:,}."
        )

        catalysts = [
            quote["headline"],
            "Liquidity and sector rotation remain supportive in the current tape.",
        ]
        if trend_bias == "Bullish":
            catalysts.insert(0, f"Momentum stays positive after a {change_pct:+.2f}% move.")
        elif trend_bias == "Bearish":
            catalysts.insert(0, f"Price action is weak after a {change_pct:+.2f}% move.")

        risks = [
            "Expect volatility around earnings and macro prints.",
            "Position sizing matters if the stock is near resistance.",
        ]

        return {
            "symbol": quote["symbol"],
            "name": quote["name"],
            "summary": summary,
            "recommendation": recommendation,
            "confidence": sentiment["confidence"],
            "quote": quote,
            "sentiment": sentiment,
            "news": news,
            "catalysts": catalysts,
            "risks": risks,
            "status": "ok",
        }
