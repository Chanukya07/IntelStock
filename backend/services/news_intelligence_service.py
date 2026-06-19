"""News intelligence service contract for financial news aggregation."""


class NewsIntelligenceService:
    def fetch_company_news(self, symbol: str) -> dict[str, str]:
        return {"symbol": symbol, "status": "not_implemented"}
