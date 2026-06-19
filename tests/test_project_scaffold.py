from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


REQUIRED_PATHS = [
    "frontend/pages",
    "frontend/components",
    "frontend/charts",
    "backend/api",
    "backend/services",
    "backend/agents",
    "backend/rag",
    "backend/models",
    "backend/database",
    "vectorstore",
    "data",
    "tests",
    "docs",
    "docker",
    "requirements",
]


def test_required_structure_exists() -> None:
    for rel in REQUIRED_PATHS:
        assert (ROOT / rel).exists(), f"Missing path: {rel}"


def test_required_api_routes_defined() -> None:
    routes_source = (ROOT / "backend/api/routes.py").read_text(encoding="utf-8")
    for route in [
        '"/stock"',
        '"/news"',
        '"/sentiment"',
        '"/insights"',
        '"/chat"',
        '"/portfolio"',
        '"/watchlist"',
    ]:
        assert route in routes_source


def test_key_endpoint_parameters_are_declared() -> None:
    routes_source = (ROOT / "backend/api/routes.py").read_text(encoding="utf-8")
    for signature_snippet in [
        "def get_stock(symbol: str)",
        "def get_sentiment(symbol: str)",
        "def get_insights(symbol: str)",
        "def get_portfolio(user_id: int)",
        "def get_watchlist(user_id: int)",
    ]:
        assert signature_snippet in routes_source


def test_database_tables_declared() -> None:
    schema = (ROOT / "backend/database/schema.sql").read_text(encoding="utf-8")
    for table in [
        "users",
        "stocks",
        "historical_prices",
        "news",
        "sentiment_scores",
        "watchlists",
        "insights",
        "chat_history",
        "portfolios",
    ]:
        assert f"CREATE TABLE IF NOT EXISTS {table}" in schema
