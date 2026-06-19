import ast
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


def _routes_module() -> ast.Module:
    source = (ROOT / "backend/api/routes.py").read_text(encoding="utf-8")
    return ast.parse(source)


def test_required_structure_exists() -> None:
    for rel in REQUIRED_PATHS:
        assert (ROOT / rel).exists(), f"Missing path: {rel}"


def test_required_api_routes_defined() -> None:
    module = _routes_module()
    found_routes = set()

    for node in module.body:
        if isinstance(node, ast.FunctionDef):
            for decorator in node.decorator_list:
                if (
                    isinstance(decorator, ast.Call)
                    and isinstance(decorator.func, ast.Attribute)
                    and isinstance(decorator.func.value, ast.Name)
                    and decorator.func.value.id == "router"
                    and decorator.args
                    and isinstance(decorator.args[0], ast.Constant)
                    and isinstance(decorator.args[0].value, str)
                ):
                    found_routes.add(decorator.args[0].value)

    for route in [
        "/stock",
        "/news",
        "/sentiment",
        "/insights",
        "/chat",
        "/portfolio",
        "/watchlist",
    ]:
        assert route in found_routes


def test_key_endpoint_parameters_are_declared() -> None:
    module = _routes_module()
    signatures = {}

    for node in module.body:
        if isinstance(node, ast.FunctionDef):
            signatures[node.name] = [arg.arg for arg in node.args.args]

    assert signatures["get_stock"] == ["symbol"]
    assert signatures["get_news"] == ["symbol", "source"]
    assert signatures["get_sentiment"] == ["symbol"]
    assert signatures["get_insights"] == ["symbol"]
    assert signatures["get_portfolio"] == ["user_id"]
    assert signatures["get_watchlist"] == ["user_id"]


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
