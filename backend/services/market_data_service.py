"""Market data service for lightweight stock intelligence."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class MarketProfile:
    symbol: str
    name: str
    sector: str
    price: float
    change_pct: float
    volume: str
    support: float
    resistance: float
    sentiment: str
    headline: str


MARKET_PROFILES: dict[str, MarketProfile] = {
    "RELIANCE": MarketProfile(
        symbol="RELIANCE",
        name="Reliance Industries",
        sector="Energy",
        price=2987.0,
        change_pct=2.4,
        volume="4.2M",
        support=2880.0,
        resistance=3050.0,
        sentiment="Bullish",
        headline="Jio and retail momentum continue to support earnings visibility.",
    ),
    "TCS": MarketProfile(
        symbol="TCS",
        name="Tata Consultancy Services",
        sector="IT",
        price=4124.0,
        change_pct=1.8,
        volume="1.8M",
        support=3980.0,
        resistance=4280.0,
        sentiment="Bullish",
        headline="Large deal wins and margin resilience keep the IT thesis intact.",
    ),
    "INFY": MarketProfile(
        symbol="INFY",
        name="Infosys",
        sector="IT",
        price=1925.0,
        change_pct=3.1,
        volume="3.3M",
        support=1860.0,
        resistance=2006.0,
        sentiment="Bullish",
        headline="Guidance upgrades and a breakout in price action support momentum.",
    ),
    "WIPRO": MarketProfile(
        symbol="WIPRO",
        name="Wipro",
        sector="IT",
        price=548.0,
        change_pct=-0.4,
        volume="2.7M",
        support=522.0,
        resistance=593.0,
        sentiment="Neutral",
        headline="Operating leverage is improving, but deal conversion remains uneven.",
    ),
    "HDFCBANK": MarketProfile(
        symbol="HDFCBANK",
        name="HDFC Bank",
        sector="Banking",
        price=1680.0,
        change_pct=-0.9,
        volume="6.1M",
        support=1648.0,
        resistance=1795.0,
        sentiment="Neutral",
        headline="Integration progress is steady, while near-term NIM pressure persists.",
    ),
    "NIFTY": MarketProfile(
        symbol="NIFTY",
        name="Nifty 50",
        sector="Broad Market",
        price=24762.0,
        change_pct=1.24,
        volume="52.4M",
        support=24400.0,
        resistance=25000.0,
        sentiment="Bullish",
        headline="Breadth and institutional flows continue to support the index trend.",
    ),
}

ALIASES = {
    "HDFC": "HDFCBANK",
    "HDFC BANK": "HDFCBANK",
    "NIFTY 50": "NIFTY",
}


def _normalize_symbol(symbol: str) -> str:
    token = symbol.strip().upper().replace(".", "")
    return ALIASES.get(token, token)


def _fallback_profile(symbol: str) -> MarketProfile:
    seed = sum(ord(char) for char in symbol)
    price = round(180 + (seed % 700) * 3.25, 2)
    change = round(((seed % 11) - 5) * 0.37, 2)
    support = round(price * 0.96, 2)
    resistance = round(price * 1.04, 2)
    sentiment = "Bullish" if change > 0.5 else "Bearish" if change < -0.5 else "Neutral"
    return MarketProfile(
        symbol=symbol,
        name=f"{symbol} Holdings",
        sector="Diversified",
        price=price,
        change_pct=change,
        volume=f"{1 + (seed % 9)}.{seed % 10}M",
        support=support,
        resistance=resistance,
        sentiment=sentiment,
        headline="Synthetic market snapshot generated from the available symbol data.",
    )


class MarketDataService:
    def fetch_live_quote(self, symbol: str) -> dict[str, str | float]:
        normalized = _normalize_symbol(symbol)
        profile = MARKET_PROFILES.get(normalized) or _fallback_profile(normalized)
        return {
            "symbol": profile.symbol,
            "name": profile.name,
            "sector": profile.sector,
            "price": profile.price,
            "change_pct": profile.change_pct,
            "volume": profile.volume,
            "support": profile.support,
            "resistance": profile.resistance,
            "sentiment": profile.sentiment,
            "headline": profile.headline,
            "status": "ok",
        }
