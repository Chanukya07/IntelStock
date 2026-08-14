"""Chat service with streaming support for real-time responses."""

from __future__ import annotations

import logging
from collections.abc import Iterator

from openai import OpenAI

from backend.config import OPENROUTER_API_BASE, OPENROUTER_API_KEY, LLM_MODEL
from backend.rag.retriever import RAGRetriever
from backend.services.insight_service import InsightService
from backend.services.market_data_service import MarketDataService
from backend.services.news_intelligence_service import NewsIntelligenceService

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "You are an expert stock analyst for Indian markets (NSE/BSE). "
    "Provide clear, actionable investment insights with specific catalysts and risks."
)

FALLBACK_NOTICE = (
    "AI analysis is unavailable right now, so here is a data-only briefing "
    "from the latest market and news data."
)


class ChatService:
    def __init__(self) -> None:
        """Initialize chat service with streaming support."""
        self._client: OpenAI | None = None
        # True when the most recent chat_stream() on this instance fell back to the
        # non-LLM briefing, so callers can avoid presenting it as a model answer.
        self.last_response_degraded = False
        self.insight_service = InsightService()
        self.market_data_service = MarketDataService()
        self.news_service = NewsIntelligenceService()
        self.rag_retriever = RAGRetriever()

    @property
    def client(self) -> OpenAI:
        """Lazy-initialize OpenAI client only when first needed."""
        if self._client is None:
            if not OPENROUTER_API_KEY:
                raise RuntimeError(
                    "OPENROUTER_API_KEY not set. Configure it in .env to enable AI chat."
                )
            self._client = OpenAI(api_key=OPENROUTER_API_KEY, base_url=OPENROUTER_API_BASE)
        return self._client

    def _infer_symbol(self, query: str) -> str:
        """Extract stock symbol from query."""
        normalized = query.upper()
        symbols = ("RELIANCE", "TCS", "INFY", "WIPRO", "HDFC", "HDFCBANK", "NIFTY")
        for symbol in symbols:
            if symbol in normalized:
                return symbol
        # Keep these tokens in sync with frontend/pages/ai_chat.py's infer_symbol, or
        # the metadata card names one stock while the answer is grounded on another.
        if any(token in normalized for token in ("INDEX", "MARKET", "NSE", "SENSEX", "FII", "IT STOCKS", "SECTOR")):
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

    def _collect_grounding(self, symbol: str, query: str) -> dict[str, object]:
        """Fetch the non-LLM grounding data (quote, headlines, RAG context).

        Deliberately avoids calling the LLM so that streaming costs exactly one
        model round-trip. Never raises: a data-source outage must degrade the
        answer, not crash the caller's generator mid-stream.
        """
        quote: dict = {}
        headlines: list[str] = []
        rag_context = ""
        try:
            quote = self.market_data_service.fetch_live_quote(symbol)
        except Exception:
            logger.warning("quote lookup failed for %s", symbol, exc_info=True)
        try:
            news = self.news_service.fetch_company_news(symbol)
            if isinstance(news, dict):
                headlines = list(news.get("headlines") or [])
        except Exception:
            logger.warning("news lookup failed for %s", symbol, exc_info=True)
        try:
            rag_context = self.rag_retriever.retrieve_symbol_context(symbol, query, top_k=3)
        except Exception:
            logger.warning("RAG retrieval failed for %s", symbol, exc_info=True)
        return {"quote": quote, "headlines": headlines, "rag_context": rag_context}

    def _build_context(self, grounding: dict[str, object]) -> str:
        """Render the grounding data as the prompt context block."""
        quote = grounding["quote"]
        headlines = grounding["headlines"]
        rag_context = grounding["rag_context"]

        parts: list[str] = []
        if quote:
            parts.extend([
                f"Stock: {quote['name']} ({quote['symbol']})",
                f"Price: ₹{quote['price']:,}  Change: {quote['change_pct']:+.2f}%",
                f"Support / Resistance: ₹{quote['support']:,} / ₹{quote['resistance']:,}",
            ])
        if headlines:
            parts.append("Recent headlines:\n- " + "\n- ".join(headlines[:5]))
        if rag_context:
            parts.append(f"Retrieved context:\n{rag_context[:600]}")
        return "\n".join(parts)

    def _fallback_chunks(self, grounding: dict[str, object]) -> list[str]:
        """Build a deterministic briefing from data already in hand.

        Uses only the grounding already fetched for the prompt — no second model
        call, no re-fetch — and is chunked so the UI keeps animating.
        """
        quote = grounding["quote"]
        headlines = grounding["headlines"]
        rag_context = grounding["rag_context"]

        if not quote:
            return [
                FALLBACK_NOTICE,
                " No market data could be retrieved either — please try again shortly.",
            ]

        change_pct = float(quote.get("change_pct", 0.0) or 0.0)
        bias = "bullish" if change_pct > 0.75 else "bearish" if change_pct < -0.75 else "neutral"
        chunks = [
            f"{FALLBACK_NOTICE}\n\n",
            f"{quote['name']} ({quote['symbol']}) is trading at ₹{quote['price']:,} "
            f"({change_pct:+.2f}%), a {bias} read on the session.\n",
            f"Nearest levels sit around ₹{quote['support']:,} support and "
            f"₹{quote['resistance']:,} resistance, with a "
            f"{str(quote.get('sentiment', 'Neutral')).lower()} sentiment tag.\n\n",
        ]
        if headlines:
            chunks.append("Recent headlines:\n- " + "\n- ".join(headlines[:3]) + "\n\n")
        if rag_context:
            chunks.append(f"Related context:\n{rag_context[:400]}\n\n")
        chunks.append(
            "Configure OPENROUTER_API_KEY and restore network access to get the full AI analysis."
        )
        return chunks

    def chat_stream(self, query: str) -> Iterator[str]:
        """Stream a chat response token-by-token via the OpenAI-compatible API.

        Falls back to a grounded, non-LLM briefing when the provider is
        unreachable or unkeyed. Provider exception text is logged, never yielded:
        the frontend renders message content as HTML.
        """
        self.last_response_degraded = False
        symbol = self._infer_symbol(query)
        grounding = self._collect_grounding(symbol, query)
        context = self._build_context(grounding)

        emitted = False
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
                    emitted = True
                    yield delta.content
        except Exception:  # noqa: BLE001 - any provider failure degrades gracefully
            logger.warning("chat_stream LLM failure for %s", symbol, exc_info=True)
            self.last_response_degraded = True
            if emitted:
                # A partial real answer is already on screen; don't staple a canned
                # briefing onto it, just mark where it stopped.
                yield "\n\n(response truncated — the model connection dropped)"
                return
            yield from self._fallback_chunks(grounding)
            return

        if not emitted:
            # Provider answered but sent nothing usable — an empty bubble is worse
            # than the deterministic briefing.
            logger.warning("chat_stream produced no content for %s", symbol)
            self.last_response_degraded = True
            yield from self._fallback_chunks(grounding)

    def get_rag_context(self, query: str, symbol: str = "") -> str:
        """Retrieve RAG context for a query."""
        if not symbol:
            symbol = self._infer_symbol(query)
        return self.rag_retriever.retrieve_symbol_context(symbol, query, top_k=3)
