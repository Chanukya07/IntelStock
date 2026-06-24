"""Insight service for AI investment reports."""
from __future__ import annotations

from openai import OpenAI

from backend.config import OPENROUTER_API_BASE, OPENROUTER_API_KEY, LLM_MODEL
from backend.rag.retriever import RAGRetriever
from backend.services.market_data_service import MarketDataService
from backend.services.news_intelligence_service import NewsIntelligenceService
from backend.services.sentiment_service import SentimentService


class InsightService:
    def __init__(self) -> None:
        self.market_data_service = MarketDataService()
        self.news_service = NewsIntelligenceService()
        self.sentiment_service = SentimentService()
        self._client = None
        self.rag_retriever = RAGRetriever()

    def _get_client(self):
        """Lazy initialization of OpenAI client only when API key is available."""
        if self._client is None:
            if not OPENROUTER_API_KEY:
                raise ValueError(
                    "OPENROUTER_API_KEY is not set. Add it to Streamlit secrets."
                )
            self._client = OpenAI(api_key=OPENROUTER_API_KEY, base_url=OPENROUTER_API_BASE)
        return self._client

    def _generate_ai_recommendation(
        self,
        quote: dict,
        sentiment: dict,
        news_text: str,
        query: str | None = None,
        symbol: str = "",
    ) -> tuple[str, list[str], list[str]]:
        """Generate AI-powered recommendation using RAG context."""
        rag_context = ""
        if symbol:
            self.rag_retriever.index_news(news_text.split('\n') if news_text else [], symbol=symbol)
        retrieved_query = query if query else f"Investment analysis for {quote['name']}"
        rag_context = self.rag_retriever.retrieve_symbol_context(symbol, retrieved_query, top_k=3)
        prompt = (
            f"You are an expert stock analyst for Indian markets (NSE/BSE).\n"
            f"Stock: {quote['name']} ({quote['symbol']})\n"
            f"Price: {quote['price']:,} Change: {quote['change_pct']:+.2f}%\n"
            f"Support: {quote['support']:,} Resistance: {quote['resistance']:,}\n"
            f"Sentiment: {sentiment['label']} Confidence: {sentiment['confidence']:.2f}\n"
            f"News: {news_text[:300] if news_text else 'No recent news'}\n"
            f"{('Context: ' + rag_context[:500]) if rag_context else ''}\n"
            f"Query: {query if query else 'General analysis'}\n\n"
            f"Respond ONLY:\nRECOMMENDATION: [recommendation]\n"
            f"CATALYSTS: [c1|c2|c3]\nRISKS: [r1|r2|r3]"
        )
        try:
            client = self._get_client()
            response = client.chat.completions.create(
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
        recommendation, catalysts, risks = self._generate_ai_recommendation(
            quote, sentiment, news_text, query, symbol
        )
        summary = (
            f"{quote['name']} is showing {trend_bias.lower()} momentum "
            f"with price at {quote['price']:,}. "
            f"Sentiment reads {sentiment['label'].lower()} and the nearest levels sit around "
            f"{quote['support']:,} / {quote['resistance']:,}."
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
