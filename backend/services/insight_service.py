"""Insight service contract for AI investment reports."""


class InsightService:
    def generate_report(self, symbol: str) -> dict[str, str]:
        return {"symbol": symbol, "status": "not_implemented"}
