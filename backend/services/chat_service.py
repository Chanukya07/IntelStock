"""Chat service with streaming support for real-time responses."""

from __future__ import annotations

from collections.abc import Iterator

from openai import OpenAI

from backend.config import OPENROUTER_API_BASE, OPENROUTER_API_KEY, LLM_MODEL
from backend.rag.retriever import RAGRetriever
from backend.services.insight_service import InsightService
from backend.services.market_data_service import MarketDataService
from backend.services.news_intelligence_service import NewsIntelligenceService

SYSTEM_PROMPT = (
    "You are an expert stock analyst for Indian markets (NSE/BSE). "
    "Provide clear, actionable investment insights with specific catalysts and risks."
)


class ChatService:
    def __init__(self) -> None:
        """Initialize chat service with streaming support."""
        self.client = OpenAI(api_key=OPENROUTER_API_KEY, base_url=OPENROUTER_API_BASE)
        self.insight_service = InsightService()
        self.market_data_service = MarketDataService()
        self.news_service = NewsIntelligenceService()
        self.rag_retriever = RAGRetriever()

    def _infer_symbol(self, query: str) -> str:
        """Extract stock symbol from query."""
        normalized = query.upper()
        symbols = ("RELIANCE", "TCS", "INFY", "WIPRO", "HDFC", "HDFCBANK", "NIFTY")
        for symbol in symbols:
            if symbol in normalized:
                return symbol
        if any(token in normalized for token in ("INDEX", "MARKET", "NSE", "SENSEX")):
            return "NIFTY"
        return "RELIANCE"

    def chat(self, query: str) -> dict[str, str]:
        """Non-streaming chat response built from the full insight report."""
        symbol = self._infer_symbol(query)
        report = self.insight_service.generate_report(symbol, query)

        return {
            "symbol": symbol,
            "message": report["summary"],
            "recommendation": report["recommendation"],
            "confidence": str(report["confidence"]),
            "catalysts": "|".join(report["catalysts"]),
            "risks": "|".join(report["risks"]),
        }

    def _build_context(self, symbol: str, query: str) -> str:
        """Assemble grounding context for the model from non-LLM data sources.

        Deliberately avoids calling the LLM here so that streaming costs exactly
        one model round-trip. Pulls the market profile, recent headlines and any
        retrieved RAG context.
        """
        quote = self.market_data_service.fetch_live_quote(symbol)
        news = self.news_service.fetch_company_news(symbol)
        headlines = news.get("headlines", []) if isinstance(news, dict) else []
        rag_context = self.rag_retriever.retrieve_symbol_context(symbol, query, top_k=3)

        parts = [
            f"Stock: {quote['name']} ({quote['symbol']})",
            f"Price: ₹{quote['price']:,}  Change: {quote['change_pct']:+.2f}%",
            f"Support / Resistance: ₹{quote['support']:,} / ₹{quote['resistance']:,}",
        ]
        if headlines:
            parts.append("Recent headlines:\n- " + "\n- ".join(headlines[:5]))
        if rag_context:
            parts.append(f"Retrieved context:\n{rag_context[:600]}")
        return "\n".join(parts)

    def chat_stream(self, query: str) -> Iterator[str]:
        """Stream a chat response token-by-token via the OpenAI-compatible API."""
        symbol = self._infer_symbol(query)
        context = self._build_context(symbol, query)

        try:
            stream = self.client.chat.completions.create(
                model=LLM_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"{context}\n\nUser Question: {query}"},
                ],
                stream=True,
                temperature=0.7,
                max_tokens=1000,
            )
            for chunk in stream:
                if not chunk.choices:
                    continue
                delta = chunk.choices[0].delta
                if delta and delta.content:
                    yield delta.content
        except Exception as e:  # noqa: BLE001 - surface provider errors to the client
            yield f"Error generating response: {e}"

    def get_rag_context(self, query: str, symbol: str = "") -> str:
        """Retrieve RAG context for a query."""
        if not symbol:
            symbol = self._infer_symbol(query)
        return self.rag_retriever.retrieve_symbol_context(symbol, query, top_k=3)
