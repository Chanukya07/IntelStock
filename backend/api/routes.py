"""API routes for IntelStock MVP surface."""

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.database import (
    get_db,
    ChatRepository,
    InsightRepository,
    PortfolioRepository,
    StockRepository,
    WatchlistRepository,
)
from backend.rag.retriever import RAGRetriever
from backend.services.chat_service import ChatService
from backend.services.insight_service import InsightService
from backend.services.market_data_service import MarketDataService
from backend.services.news_intelligence_service import NewsIntelligenceService
from backend.services.sentiment_service import SentimentService

router = APIRouter()
market_data_service = MarketDataService()
news_service = NewsIntelligenceService()
sentiment_service = SentimentService()
insight_service = InsightService()
rag_retriever = RAGRetriever()
chat_service = ChatService()


class ChatRequest(BaseModel):
    query: str


class IndexDocumentRequest(BaseModel):
    text: str
    symbol: str = ""
    title: str = ""


class RAGQueryRequest(BaseModel):
    query: str
    symbol: str = ""
    top_k: int = 5


class PortfolioItem(BaseModel):
    symbol: str
    quantity: float
    average_cost: float


class WatchlistItem(BaseModel):
    symbol: str


@router.get("/stock")
def get_stock(symbol: str) -> dict[str, str | float]:
    return market_data_service.fetch_live_quote(symbol)


@router.get("/news")
def get_news(symbol: str, source: str | None = None) -> dict[str, object]:
    news = news_service.fetch_company_news(symbol)
    if source:
        news["source"] = source
    return news


@router.get("/sentiment")
def get_sentiment(symbol: str) -> dict[str, object]:
    quote = market_data_service.fetch_live_quote(symbol)
    narrative = f"{quote['name']} shows {quote['sentiment'].lower()} momentum with a {quote['change_pct']:+.2f}% move."
    return sentiment_service.score_news(f"{quote['headline']} {narrative}") | {"symbol": quote["symbol"]}


@router.get("/insights")
def get_insights(symbol: str) -> dict[str, object]:
    return insight_service.generate_report(symbol)


@router.post("/chat")
def chat(payload: ChatRequest, db: Session = Depends(get_db)) -> dict[str, object]:
    result = chat_service.chat(payload.query)
    # Persist the exchange (user_id is optional until auth lands).
    ChatRepository(db).create(prompt=payload.query, response=result["message"])
    return result


@router.post("/chat/stream")
def chat_stream(payload: ChatRequest) -> StreamingResponse:
    """Stream chat response for real-time updates."""
    return StreamingResponse(
        chat_service.chat_stream(payload.query),
        media_type="text/event-stream",
    )


@router.get("/portfolio")
def get_portfolio(user_id: int, db: Session = Depends(get_db)) -> dict[str, object]:
    """Get user's portfolio with live mark-to-market P&L."""
    holdings = PortfolioRepository(db).get_user_portfolio(user_id)

    items: list[dict[str, object]] = []
    total_value = 0.0
    for holding in holdings:
        symbol = holding.stock.symbol
        quantity = float(holding.quantity)
        avg_price = float(holding.avg_price)
        current_price = float(market_data_service.fetch_live_quote(symbol)["price"])
        market_value = current_price * quantity
        total_value += market_value
        items.append(
            {
                "id": holding.id,
                "symbol": symbol,
                "quantity": quantity,
                "avg_price": avg_price,
                "current_price": current_price,
                "market_value": round(market_value, 2),
                "gain_loss": round((current_price - avg_price) * quantity, 2),
            }
        )

    return {"user_id": user_id, "portfolio": items, "total_value": round(total_value, 2)}


@router.post("/portfolio")
def add_portfolio(user_id: int, item: PortfolioItem, db: Session = Depends(get_db)) -> dict[str, object]:
    """Add a holding to the user's portfolio."""
    quote = market_data_service.fetch_live_quote(item.symbol)
    stock = StockRepository(db).get_or_create(item.symbol, company_name=quote.get("name"))
    holding = PortfolioRepository(db).create(user_id, stock.id, item.quantity, item.average_cost)
    return {"status": "ok", "portfolio_id": holding.id, "symbol": item.symbol}


@router.get("/watchlist")
def get_watchlist(user_id: int, db: Session = Depends(get_db)) -> dict[str, object]:
    """Get user's watchlist."""
    entries = WatchlistRepository(db).get_user_watchlist(user_id)
    return {
        "user_id": user_id,
        "watchlist": [{"id": w.id, "symbol": w.stock.symbol} for w in entries],
    }


@router.post("/watchlist")
def add_watchlist(user_id: int, item: WatchlistItem, db: Session = Depends(get_db)) -> dict[str, object]:
    """Add a stock to the user's watchlist."""
    quote = market_data_service.fetch_live_quote(item.symbol)
    stock = StockRepository(db).get_or_create(item.symbol, company_name=quote.get("name"))
    entry = WatchlistRepository(db).create(user_id, stock.id)
    return {"status": "ok", "watchlist_id": entry.id, "symbol": item.symbol}


@router.delete("/watchlist/{watchlist_id}")
def remove_watchlist(watchlist_id: int, db: Session = Depends(get_db)) -> dict[str, str]:
    """Remove a stock from the user's watchlist."""
    success = WatchlistRepository(db).delete(watchlist_id)
    return {"status": "ok" if success else "error", "message": "Item removed" if success else "Item not found"}


@router.post("/rag/index")
def index_document(payload: IndexDocumentRequest) -> dict[str, str]:
    """Index a document for RAG retrieval."""
    rag_retriever.index_document(payload.text, symbol=payload.symbol, title=payload.title)
    return {"status": "ok", "message": f"Document indexed for {payload.symbol or 'general'} analysis"}


@router.post("/rag/search")
def search_rag(payload: RAGQueryRequest) -> dict[str, object]:
    """Search indexed documents using RAG."""
    if payload.symbol:
        context = rag_retriever.retrieve_symbol_context(payload.symbol, payload.query, top_k=payload.top_k)
    else:
        context = rag_retriever.retrieve_context(payload.query, top_k=payload.top_k)

    return {"status": "ok", "query": payload.query, "context": context}


@router.delete("/rag/clear")
def clear_rag_index() -> dict[str, str]:
    """Clear all indexed documents."""
    rag_retriever.clear_index()
    return {"status": "ok", "message": "RAG index cleared"}


@router.post("/rag/context")
def get_rag_context(payload: RAGQueryRequest) -> dict[str, object]:
    """Get RAG context for a query."""
    context = chat_service.get_rag_context(payload.query, payload.symbol)
    return {"status": "ok", "query": payload.query, "context": context}
