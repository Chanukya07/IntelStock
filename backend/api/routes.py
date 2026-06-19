"""API routes for IntelStock MVP surface."""

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.database import (
    get_db, PortfolioRepository, WatchlistRepository,
    ChatRepository, StockQuoteRepository, InsightRepository
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
    quantity: int
    average_cost: float


class WatchlistItem(BaseModel):
    symbol: str
    alert_price: float | None = None
    alert_type: str | None = None


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


def _infer_symbol(query: str) -> str:
    normalized = query.upper()
    for symbol in ("RELIANCE", "TCS", "INFY", "WIPRO", "HDFC", "HDFCBANK", "NIFTY"):
        if symbol in normalized:
            return symbol
    if any(token in normalized for token in ("INDEX", "MARKET", "NSE", "SENSEX")):
        return "NIFTY"
    return "RELIANCE"


@router.post("/chat")
def chat(payload: ChatRequest) -> dict[str, object]:
    return chat_service.chat(payload.query)


@router.post("/chat/stream")
def chat_stream(payload: ChatRequest) -> StreamingResponse:
    """Stream chat response for real-time updates."""
    return StreamingResponse(
        chat_service.chat_stream(payload.query),
        media_type="text/event-stream",
    )


@router.get("/portfolio")
def get_portfolio(user_id: int, db: Session = Depends(get_db)) -> dict[str, object]:
    """Get user's portfolio."""
    repo = PortfolioRepository(db)
    portfolio = repo.get_user_portfolio(user_id)
    total_value = sum(p.current_price * p.quantity for p in portfolio if p.current_price)
    return {
        "user_id": user_id,
        "portfolio": [
            {
                "id": p.id,
                "symbol": p.symbol,
                "quantity": p.quantity,
                "average_cost": p.average_cost,
                "current_price": p.current_price,
                "gain_loss": (p.current_price - p.average_cost) * p.quantity if p.current_price else 0,
            }
            for p in portfolio
        ],
        "total_value": total_value,
    }


@router.post("/portfolio")
def add_portfolio(user_id: int, item: PortfolioItem, db: Session = Depends(get_db)) -> dict[str, object]:
    """Add stock to portfolio."""
    repo = PortfolioRepository(db)
    portfolio = repo.create(user_id, item.symbol, item.quantity, item.average_cost)
    return {"status": "ok", "portfolio_id": portfolio.id}


@router.get("/watchlist")
def get_watchlist(user_id: int, db: Session = Depends(get_db)) -> dict[str, object]:
    """Get user's watchlist."""
    repo = WatchlistRepository(db)
    watchlist = repo.get_user_watchlist(user_id)
    return {
        "user_id": user_id,
        "watchlist": [
            {
                "id": w.id,
                "symbol": w.symbol,
                "alert_price": w.alert_price,
                "alert_type": w.alert_type,
            }
            for w in watchlist
        ],
    }


@router.post("/watchlist")
def add_watchlist(user_id: int, item: WatchlistItem, db: Session = Depends(get_db)) -> dict[str, object]:
    """Add stock to watchlist."""
    repo = WatchlistRepository(db)
    watchlist = repo.create(user_id, item.symbol, item.alert_price, item.alert_type)
    return {"status": "ok", "watchlist_id": watchlist.id}


@router.delete("/watchlist/{watchlist_id}")
def remove_watchlist(watchlist_id: int, db: Session = Depends(get_db)) -> dict[str, str]:
    """Remove stock from watchlist."""
    repo = WatchlistRepository(db)
    success = repo.delete(watchlist_id)
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
