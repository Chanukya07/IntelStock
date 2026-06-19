"""API routes for IntelStock MVP surface."""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class ChatRequest(BaseModel):
    query: str


@router.get("/stock")
def get_stock(symbol: str) -> dict[str, str]:
    return {"symbol": symbol, "message": "Market data service placeholder"}


@router.get("/news")
def get_news(symbol: str, source: str | None = None) -> dict[str, str | None]:
    return {
        "symbol": symbol,
        "source": source,
        "message": "News intelligence service placeholder",
    }


@router.get("/sentiment")
def get_sentiment(symbol: str) -> dict[str, str]:
    return {"symbol": symbol, "message": "Sentiment analysis service placeholder"}


@router.get("/insights")
def get_insights(symbol: str) -> dict[str, str]:
    return {"symbol": symbol, "message": "LLM insight engine placeholder"}


@router.post("/chat")
def chat(payload: ChatRequest) -> dict[str, str]:
    return {"message": f"Research agent placeholder response for: {payload.query}"}


@router.get("/portfolio")
def get_portfolio(user_id: int) -> dict[str, int | str]:
    return {"user_id": user_id, "message": "Portfolio analytics placeholder"}


@router.get("/watchlist")
def get_watchlist(user_id: int) -> dict[str, int | str]:
    return {"user_id": user_id, "message": "Watchlist placeholder"}
