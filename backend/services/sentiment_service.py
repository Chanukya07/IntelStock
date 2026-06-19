"""Sentiment service contract for bullish/bearish analysis."""


class SentimentService:
    def score_news(self, text: str) -> dict[str, str]:
        return {"status": "not_implemented", "text": text}
