"""Chat service with streaming support for real-time responses."""

from __future__ import annotations

from openai import OpenAI

from backend.config import OPENROUTER_API_BASE, OPENROUTER_API_KEY, LLM_MODEL
from backend.rag.retriever import RAGRetriever
from backend.services.insight_service import InsightService


class ChatService:
    def __init__(self) -> None:
        """Initialize chat service with streaming support."""
        self.client = OpenAI(api_key=OPENROUTER_API_KEY, base_url=OPENROUTER_API_BASE)
        self.insight_service = InsightService()
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
        """Non-streaming chat response."""
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

    def chat_stream(self, query: str) -> str:
        """Stream chat response token-by-token."""
        symbol = self._infer_symbol(query)
        report = self.insight_service.generate_report(symbol, query)

        context = f"""Stock: {report['name']} ({symbol})
Price: ₹{report['quote']['price']:,}
Change: {report['quote']['change_pct']:+.2f}%
Sentiment: {report['sentiment']['label']}

{report['summary']}

Recommendation: {report['recommendation']}"""

        system_prompt = """You are an expert stock analyst for Indian markets (NSE/BSE).
Provide clear, actionable investment insights with specific catalysts and risks."""

        try:
            with self.client.chat.completions.create(
                model=LLM_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"{context}\n\nUser Question: {query}"},
                ],
                stream=True,
                temperature=0.7,
                max_tokens=1000,
            ) as stream:
                for text in stream.text_stream:
                    yield text
        except Exception as e:
            yield f"Error generating response: {str(e)}"

    def get_rag_context(self, query: str, symbol: str = "") -> str:
        """Retrieve RAG context for a query."""
        if not symbol:
            symbol = self._infer_symbol(query)

        return self.rag_retriever.retrieve_symbol_context(symbol, query, top_k=3)
