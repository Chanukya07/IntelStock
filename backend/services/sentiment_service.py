"""Sentiment service for bullish/bearish analysis."""
from __future__ import annotations

from openai import OpenAI

from backend.config import OPENROUTER_API_BASE, OPENROUTER_API_KEY, LLM_MODEL

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
    def __init__(self) -> None:
        self._client = None

    def _get_client(self):
        """Lazy initialization of OpenAI client only when API key is available."""
        if self._client is None:
            if not OPENROUTER_API_KEY:
                raise ValueError(
                    "OPENROUTER_API_KEY is not set. Add it to Streamlit secrets or environment variables."
                )
            self._client = OpenAI(api_key=OPENROUTER_API_KEY, base_url=OPENROUTER_API_BASE)
        return self._client

    def score_news(self, text: str) -> dict[str, float | str]:
        if not text or len(text.strip()) < 10:
            return {
                "status": "ok",
                "text": text,
                "bullish_score": 0.5,
                "bearish_score": 0.5,
                "label": "Neutral",
                "confidence": 0.3,
            }
        try:
            client = self._get_client()
            prompt = f"""Analyze the sentiment of this stock market news for Indian markets. Respond with ONLY:
LABEL: [Bullish/Bearish/Neutral]
BULLISH_SCORE: [0.0-1.0]
BEARISH_SCORE: [0.0-1.0]
CONFIDENCE: [0.0-1.0]

News: {text[:1000]}"""
            response = client.chat.completions.create(
                model=LLM_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=100,
            )
            content = response.choices[0].message.content
            lines = content.strip().split('\n')
            label = "Neutral"
            bullish_score = 0.5
            bearish_score = 0.5
            confidence = 0.7
            for line in lines:
                if "LABEL:" in line:
                    label = line.split("LABEL:")[-1].strip()
                elif "BULLISH_SCORE:" in line:
                    try:
                        bullish_score = float(line.split("BULLISH_SCORE:")[-1].strip())
                    except ValueError:
                        pass
                elif "BEARISH_SCORE:" in line:
                    try:
                        bearish_score = float(line.split("BEARISH_SCORE:")[-1].strip())
                    except ValueError:
                        pass
                elif "CONFIDENCE:" in line:
                    try:
                        confidence = float(line.split("CONFIDENCE:")[-1].strip())
                    except ValueError:
                        pass
            return {
                "status": "ok",
                "text": text,
                "bullish_score": round(bullish_score, 2),
                "bearish_score": round(bearish_score, 2),
                "label": label,
                "confidence": round(confidence, 2),
            }
        except Exception as e:
            print(f"AI sentiment analysis failed: {e}")
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
