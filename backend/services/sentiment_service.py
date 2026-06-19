"""Sentiment service for bullish/bearish analysis."""

from __future__ import annotations


POSITIVE_TERMS = {
    "bullish",
    "breakout",
    "buy",
    "beat",
    "growth",
    "guidance",
    "inflow",
    "momentum",
    "upgrade",
    "record",
    "resilient",
    "strong",
}

NEGATIVE_TERMS = {
    "bearish",
    "downgrade",
    "fall",
    "headwind",
    "loss",
    "pressure",
    "risk",
    "slowdown",
    "weak",
    "volatile",
}


class SentimentService:
    def score_news(self, text: str) -> dict[str, float | str]:
        normalized = text.lower()
        positive_hits = sum(1 for term in POSITIVE_TERMS if term in normalized)
        negative_hits = sum(1 for term in NEGATIVE_TERMS if term in normalized)
        total = positive_hits + negative_hits

        bullish_score = round(0.5 if total == 0 else positive_hits / total, 2)
        bearish_score = round(0.5 if total == 0 else negative_hits / total, 2)
        if bullish_score > bearish_score + 0.15:
            label = "Bullish"
        elif bearish_score > bullish_score + 0.15:
            label = "Bearish"
        else:
            label = "Neutral"

        confidence = round(min(0.95, 0.45 + total * 0.1), 2)
        return {
            "status": "ok",
            "text": text,
            "bullish_score": bullish_score,
            "bearish_score": bearish_score,
            "label": label,
            "confidence": confidence,
        }
