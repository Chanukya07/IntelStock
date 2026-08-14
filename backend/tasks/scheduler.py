"""Periodic background tasks for market data refresh and cache warm-up."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime

from backend.services.market_data_service import MarketDataService
from backend.services.sentiment_service import SentimentService
from backend.rag.retriever import RAGRetriever

logger = logging.getLogger(__name__)

TRACKED_SYMBOLS = ("RELIANCE", "TCS", "INFY", "WIPRO", "HDFC", "HDFCBANK", "NIFTY")
REFRESH_INTERVAL_SECONDS = 900  # 15 minutes


async def refresh_market_data() -> None:
    """Fetch and cache live quotes for tracked symbols."""
    logger.info("Starting market data refresh at %s", datetime.now().isoformat())
    market_data = MarketDataService()

    for symbol in TRACKED_SYMBOLS:
        try:
            market_data.fetch_live_quote(symbol)
            logger.debug("Refreshed %s", symbol)
        except Exception as e:
            logger.warning("Failed to refresh %s: %s", symbol, e)

    logger.info("Market data refresh completed")


async def warm_up_sentiment_cache() -> None:
    """Pre-compute sentiment scores for tracked symbols."""
    logger.info("Starting sentiment cache warm-up at %s", datetime.now().isoformat())
    sentiment = SentimentService()
    market_data = MarketDataService()

    for symbol in TRACKED_SYMBOLS:
        try:
            quote = market_data.fetch_live_quote(symbol)
            narrative = f"{quote['name']} shows {quote['sentiment'].lower()} momentum with a {quote['change_pct']:+.2f}% move."
            sentiment.score_news(f"{quote['headline']} {narrative}")
            logger.debug("Warmed up sentiment for %s", symbol)
        except Exception as e:
            logger.warning("Failed to warm up sentiment for %s: %s", symbol, e)

    logger.info("Sentiment cache warm-up completed")


async def refresh_rag_index() -> None:
    """Refresh RAG vector store with latest news and research."""
    logger.info("Starting RAG index refresh at %s", datetime.now().isoformat())
    rag = RAGRetriever()

    for symbol in TRACKED_SYMBOLS:
        try:
            rag.retrieve_symbol_context(symbol, "", top_k=1)
            logger.debug("Refreshed RAG context for %s", symbol)
        except Exception as e:
            logger.warning("Failed to refresh RAG context for %s: %s", symbol, e)

    logger.info("RAG index refresh completed")


async def run_background_tasks() -> None:
    """Run all background refresh tasks concurrently."""
    while True:
        try:
            await asyncio.gather(
                refresh_market_data(),
                warm_up_sentiment_cache(),
                refresh_rag_index(),
            )
        except Exception as e:
            logger.error("Background task error: %s", e)

        await asyncio.sleep(REFRESH_INTERVAL_SECONDS)
