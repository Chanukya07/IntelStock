"""News intelligence service for financial news aggregation."""

from __future__ import annotations


NEWS_FEED: dict[str, list[str]] = {
    "RELIANCE": [
        "Jio subscriptions remain resilient, supporting digital growth visibility.",
        "Retail margins are holding above street expectations into the next quarter.",
    ],
    "TCS": [
        "Large deal wins keep the order pipeline healthy for the next few quarters.",
        "Management commentary points to steady demand from North America clients.",
    ],
    "INFY": [
        "Guidance upgrades have strengthened the medium-term growth narrative.",
        "The stock continues to show leadership among large-cap IT names.",
    ],
    "HDFCBANK": [
        "Integration costs are easing, but NIM recovery remains the key watchpoint.",
        "Deposit growth is improving after a period of merger-related pressure.",
    ],
    "NIFTY": [
        "Institutional inflows are broadening across large- and mid-cap segments.",
        "Market breadth has improved, though index leadership remains selective.",
    ],
}


class NewsIntelligenceService:
    def fetch_company_news(self, symbol: str) -> dict[str, str | list[str]]:
        normalized = symbol.strip().upper()
        headlines = NEWS_FEED.get(normalized)
        if headlines is None and normalized == "HDFC":
            headlines = NEWS_FEED["HDFCBANK"]
        if headlines is None:
            headlines = [
                f"{normalized} is seeing steady investor attention ahead of the next earnings cycle.",
                f"Analysts are watching {normalized} for confirmation of margin and demand trends.",
            ]
        return {
            "symbol": normalized,
            "status": "ok",
            "headlines": headlines,
            "source": "IntelStock research brief",
        }
