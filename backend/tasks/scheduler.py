"""Periodic background tasks for market data refresh and cache warm-up."""

from __future__ import annotations

import asyncio
import logging
import threading
from datetime import datetime

from backend.services.market_data_service import MarketDataService
from backend.services.news_intelligence_service import NewsIntelligenceService
from backend.services.sentiment_service import SentimentService
from backend.rag.retriever import RAGRetriever

logger = logging.getLogger(__name__)

_alert_service = None

# The vector store writes FAISS/pickle files in place, and the in-process loop
# can now overlap a cron-triggered /api/v1/cron/refresh-rag. Serialize the
# indexing so two workers never rewrite the same files at once.
_rag_write_lock = threading.Lock()


def _get_alert_service():
    """Lazily import the alert_service singleton owned by advanced_routes.

    Deferred to avoid a hard import-order dependency at module load time —
    the same AlertService instance backing the /api/v1/alerts endpoints
    must be reused here so alerts created via the API are actually checked.
    """
    global _alert_service
    if _alert_service is None:
        from backend.api.advanced_routes import alert_service

        _alert_service = alert_service
    return _alert_service


def _index_news(rag, headlines: list[str], symbol: str) -> None:
    """Index headlines under the shared write lock (runs on a worker thread)."""
    with _rag_write_lock:
        rag.index_news(headlines, symbol=symbol)


TRACKED_SYMBOLS = ("RELIANCE", "TCS", "INFY", "WIPRO", "HDFC", "HDFCBANK", "NIFTY")
REFRESH_INTERVAL_SECONDS = 900  # 15 minutes


async def refresh_market_data(market_data: MarketDataService | None = None) -> None:
    """Fetch and cache live quotes for tracked symbols."""
    logger.info("Starting market data refresh at %s", datetime.now().isoformat())
    market_data = market_data or MarketDataService()

    for symbol in TRACKED_SYMBOLS:
        try:
            # fetch_live_quote does blocking yfinance/requests I/O; running it
            # inline would stall the event loop for the whole refresh (and for
            # the full network timeout when the host is offline).
            await asyncio.to_thread(market_data.fetch_live_quote, symbol)
            logger.debug("Refreshed %s", symbol)
        except Exception as e:
            logger.warning("Failed to refresh %s: %s", symbol, e)

    logger.info("Market data refresh completed")


async def warm_up_sentiment_cache(market_data: MarketDataService | None = None) -> None:
    """Pre-compute sentiment scores for tracked symbols."""
    logger.info("Starting sentiment cache warm-up at %s", datetime.now().isoformat())
    sentiment = SentimentService()
    market_data = market_data or MarketDataService()

    for symbol in TRACKED_SYMBOLS:
        try:
            quote = await asyncio.to_thread(market_data.fetch_live_quote, symbol)
            narrative = f"{quote['name']} shows {quote['sentiment'].lower()} momentum with a {quote['change_pct']:+.2f}% move."
            # score_news calls the OpenAI SDK synchronously.
            await asyncio.to_thread(sentiment.score_news, f"{quote['headline']} {narrative}")
            logger.debug("Warmed up sentiment for %s", symbol)
        except Exception as e:
            logger.warning("Failed to warm up sentiment for %s: %s", symbol, e)

    logger.info("Sentiment cache warm-up completed")


async def check_price_alerts(market_data: MarketDataService | None = None) -> None:
    """Evaluate active price alerts against live quotes and mark hits."""
    logger.info("Starting price alert check at %s", datetime.now().isoformat())
    alert_service = _get_alert_service()
    market_data = market_data or MarketDataService()

    for symbol in TRACKED_SYMBOLS:
        try:
            quote = await asyncio.to_thread(market_data.fetch_live_quote, symbol)
            # check_alerts opens its own DB session per call, so it is safe to
            # run on a worker thread (the session never crosses threads).
            triggered = await asyncio.to_thread(
                alert_service.check_alerts,
                symbol=quote["symbol"],
                current_price=quote["price"],
                change_pct=quote["change_pct"],
                volume=quote["volume"],
            )
            for alert in triggered:
                logger.info("Alert %s triggered for %s", alert.id, symbol)
        except Exception as e:
            logger.warning("Failed to check alerts for %s: %s", symbol, e)

    logger.info("Price alert check completed")


async def refresh_rag_index() -> None:
    """Re-index latest news headlines into the RAG vector store.

    Previously called retrieve_symbol_context(symbol, "") — a read-only
    search with an empty query, which the embedding layer short-circuits
    to an empty result. That indexed nothing; this now actually writes
    fresh headlines via index_news() so retrieval has current content.
    """
    logger.info("Starting RAG index refresh at %s", datetime.now().isoformat())
    rag = RAGRetriever()
    news_service = NewsIntelligenceService()

    for symbol in TRACKED_SYMBOLS:
        try:
            news = await asyncio.to_thread(news_service.fetch_company_news, symbol)
            headlines = news.get("headlines", [])
            if headlines:
                # Embedding + FAISS write are CPU/IO bound and synchronous.
                await asyncio.to_thread(_index_news, rag, headlines, symbol)
            logger.debug("Refreshed RAG index for %s (%d headlines)", symbol, len(headlines))
        except Exception as e:
            logger.warning("Failed to refresh RAG index for %s: %s", symbol, e)

    logger.info("RAG index refresh completed")


async def run_background_tasks() -> None:
    """Run all background refresh tasks concurrently."""
    while True:
        # One MarketDataService per round: its 60s TTL cache lets the three
        # quote-consuming jobs reuse a fetch instead of hitting the network
        # three times for every tracked symbol.
        market_data = MarketDataService()
        try:
            await asyncio.gather(
                refresh_market_data(market_data),
                warm_up_sentiment_cache(market_data),
                refresh_rag_index(),
                check_price_alerts(market_data),
            )
        except Exception as e:
            logger.error("Background task error: %s", e)

        await asyncio.sleep(REFRESH_INTERVAL_SECONDS)
