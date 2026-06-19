"""Market data service contract for live and historical stock intelligence."""


class MarketDataService:
    def fetch_live_quote(self, symbol: str) -> dict[str, str]:
        return {"symbol": symbol, "status": "not_implemented"}
