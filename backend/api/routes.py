"""API routes for IntelStock MVP surface."""

from fastapi import APIRouter
from pydantic import BaseModel

from backend.rag.retriever import RAGRetriever
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
    symbol = _infer_symbol(payload.query)
    report = insight_service.generate_report(symbol, payload.query)
    return {
        "symbol": symbol,
        "message": report["summary"],
        "recommendation": report["recommendation"],
        "confidence": report["confidence"],
        "catalysts": report["catalysts"],
        "risks": report["risks"],
    }


@router.get("/portfolio")
def get_portfolio(user_id: int) -> dict[str, int | str]:
    return {"user_id": user_id, "message": "Portfolio analytics placeholder"}


@router.get("/watchlist")
def get_watchlist(user_id: int) -> dict[str, int | str]:
    return {"user_id": user_id, "message": "Watchlist placeholder"}


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
