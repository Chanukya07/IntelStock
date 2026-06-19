"""Insight service for AI investment reports."""

from __future__ import annotations

from openai import OpenAI

from backend.config import OPENROUTER_API_BASE, OPENROUTER_API_KEY, LLM_MODEL
from backend.services.market_data_service import MarketDataService
from backend.services.news_intelligence_service import NewsIntelligenceService
from backend.services.sentiment_service import SentimentService


class InsightService:
    def __init__(self) -> None:
        self.market_data_service = MarketDataService()
        self.news_service = NewsIntelligenceService()
        self.sentiment_service = SentimentService()
        self.client = OpenAI(api_key=OPENROUTER_API_KEY, base_url=OPENROUTER_API_BASE)

    def _generate_ai_recommendation(self, quote: dict, sentiment: dict, news_text: str, query: str | None = None) -> tuple[str, list[str], list[str]]:
        """Generate AI-powered recommendation, catalysts, and risks using OpenRouter."""
        prompt = f"""You are an expert stock analyst for Indian markets (NSE/BSE). Analyze the following data and provide investment insights:

Stock: {quote['name']} ({quote['symbol']})
Current Price: ₹{quote['price']:,}
Change: {quote['change_pct']:+.2f}%
Support: ₹{quote['support']:,}
Resistance: ₹{quote['resistance']:,}
Sentiment: {sentiment['label']}
Confidence: {sentiment['confidence']:.2f}

Recent News: {news_text[:500] if news_text else 'No recent news'}

User Query: {query if query else 'General analysis'}

Provide your response in this exact format:
RECOMMENDATION: [specific actionable recommendation]
CATALYSTS: [list 2-3 positive catalysts separated by |]
RISKS: [list 2-3 risks separated by |]"""

        try:
            response = self.client.chat.completions.create(
                model=LLM_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=500,
            )

            content = response.choices[0].message.content
            lines = content.strip().split('\n')

            recommendation = "Hold and monitor for opportunities"
            catalysts = ["Market momentum", "Sector strength"]
            risks = ["Market volatility", "Earnings risk"]

            for line in lines:
                if line.startswith("RECOMMENDATION:"):
                    recommendation = line.replace("RECOMMENDATION:", "").strip()
                elif line.startswith("CATALYSTS:"):
                    catalysts = [c.strip() for c in line.replace("CATALYSTS:", "").split("|")]
                elif line.startswith("RISKS:"):
                    risks = [r.strip() for r in line.replace("RISKS:", "").split("|")]

            return recommendation, catalysts, risks
        except Exception as e:
            print(f"AI generation failed: {e}")
            return "Hold and monitor for opportunities", ["Market momentum"], ["Market volatility"]

    def generate_report(self, symbol: str, query: str | None = None) -> dict[str, object]:
        quote = self.market_data_service.fetch_live_quote(symbol)
        news = self.news_service.fetch_company_news(symbol)
        news_text = " ".join(news["headlines"]) if isinstance(news.get("headlines"), list) else ""
        sentiment = self.sentiment_service.score_news(news_text)

        change_pct = float(quote["change_pct"])
        trend_bias = "Bullish" if change_pct > 0.75 else "Bearish" if change_pct < -0.75 else "Neutral"

        # Generate AI-powered insights
        recommendation, catalysts, risks = self._generate_ai_recommendation(quote, sentiment, news_text, query)

        summary = (
            f"{quote['name']} is showing {trend_bias.lower()} momentum with price at ₹{quote['price']:,}. "
            f"Sentiment reads {sentiment['label'].lower()} and the nearest levels sit around "
            f"₹{quote['support']:,} / ₹{quote['resistance']:,}."
        )

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
