"""API routes for IntelStock MVP surface."""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class ChatRequest(BaseModel):
    query: str


@router.get("/stock")
def get_stock() -> dict[str, str]:
    return {"message": "Market data service placeholder"}


@router.get("/news")
def get_news() -> dict[str, str]:
    return {"message": "News intelligence service placeholder"}


@router.get("/sentiment")
def get_sentiment() -> dict[str, str]:
    return {"message": "Sentiment analysis service placeholder"}


@router.get("/insights")
def get_insights() -> dict[str, str]:
    return {"message": "LLM insight engine placeholder"}


@router.post("/chat")
def chat(payload: ChatRequest) -> dict[str, str]:
    return {"message": f"Research agent placeholder response for: {payload.query}"}


@router.get("/portfolio")
def get_portfolio() -> dict[str, str]:
    return {"message": "Portfolio analytics placeholder"}


@router.get("/watchlist")
def get_watchlist() -> dict[str, str]:
    return {"message": "Watchlist placeholder"}
