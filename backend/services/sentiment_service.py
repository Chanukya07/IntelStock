"""Sentiment service contract for bullish/bearish analysis."""


class SentimentService:
    def score_news(self, text: str) -> dict[str, float | str]:
        return {
            "status": "not_implemented",
            "text": text,
            "bullish_score": 0.0,
            "bearish_score": 0.0,
        }
