"""Request validators for API inputs."""

from __future__ import annotations

from fastapi import HTTPException


VALID_SYMBOLS = {"RELIANCE", "TCS", "INFY", "WIPRO", "HDFC", "HDFCBANK", "NIFTY"}
MAX_QUERY_LENGTH = 500
MAX_DOCUMENT_LENGTH = 50000
MAX_TOP_K = 100
MIN_QUANTITY = 0.1
MAX_QUANTITY = 10000
MIN_PRICE = 0.01
MAX_PRICE = 100000


def validate_symbol(symbol: str) -> str:
    """Validate and normalize stock symbol."""
    if not symbol or not isinstance(symbol, str):
        raise HTTPException(status_code=400, detail="Symbol must be a non-empty string")

    normalized = symbol.strip().upper()
    if len(normalized) > 20:
        raise HTTPException(status_code=400, detail="Symbol too long (max 20 chars)")

    if not normalized.replace("_", "").isalnum():
        raise HTTPException(status_code=400, detail="Symbol contains invalid characters")

    return normalized


def validate_query(query: str) -> str:
    """Validate search/chat query."""
    if not query or not isinstance(query, str):
        raise HTTPException(status_code=400, detail="Query must be a non-empty string")

    query = query.strip()
    if len(query) > MAX_QUERY_LENGTH:
        raise HTTPException(
            status_code=400, detail=f"Query too long (max {MAX_QUERY_LENGTH} chars)"
        )

    if len(query) < 2:
        raise HTTPException(status_code=400, detail="Query too short (min 2 chars)")

    return query


def validate_user_id(user_id: int) -> int:
    """Validate user ID."""
    if not isinstance(user_id, int) or user_id <= 0:
        raise HTTPException(status_code=400, detail="User ID must be a positive integer")
    return user_id


def validate_document_text(text: str) -> str:
    """Validate document text for indexing."""
    if not text or not isinstance(text, str):
        raise HTTPException(status_code=400, detail="Text must be a non-empty string")

    text = text.strip()
    if len(text) > MAX_DOCUMENT_LENGTH:
        raise HTTPException(
            status_code=400, detail=f"Document too large (max {MAX_DOCUMENT_LENGTH} chars)"
        )

    if len(text) < 10:
        raise HTTPException(status_code=400, detail="Document too short (min 10 chars)")

    return text


def validate_top_k(top_k: int) -> int:
    """Validate top_k parameter for retrieval."""
    if not isinstance(top_k, int) or top_k <= 0:
        raise HTTPException(status_code=400, detail="top_k must be a positive integer")

    if top_k > MAX_TOP_K:
        raise HTTPException(status_code=400, detail=f"top_k too large (max {MAX_TOP_K})")

    return top_k


def validate_portfolio_item(symbol: str, quantity: float, avg_price: float) -> tuple[str, float, float]:
    """Validate portfolio item data."""
    symbol = validate_symbol(symbol)

    if not isinstance(quantity, (int, float)) or quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be a positive number")

    if quantity < MIN_QUANTITY or quantity > MAX_QUANTITY:
        raise HTTPException(
            status_code=400, detail=f"Quantity out of range ({MIN_QUANTITY}-{MAX_QUANTITY})"
        )

    if not isinstance(avg_price, (int, float)) or avg_price <= 0:
        raise HTTPException(status_code=400, detail="Average price must be a positive number")

    if avg_price < MIN_PRICE or avg_price > MAX_PRICE:
        raise HTTPException(
            status_code=400, detail=f"Price out of range (₹{MIN_PRICE}-₹{MAX_PRICE})"
        )

    return symbol, float(quantity), float(avg_price)
