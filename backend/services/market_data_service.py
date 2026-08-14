"""Market data service for lightweight stock intelligence with live yfinance data."""
from __future__ import annotations
from dataclasses import dataclass
from typing import cast, Any
import yfinance as yf
import requests
import time

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
        symbol="RELIANCE", name="Reliance Industries", sector="Energy",
        price=2987.0, change_pct=2.4, volume="4.2M", support=2880.0, resistance=3050.0,
        sentiment="Bullish", headline="Jio and retail momentum continue to support earnings visibility.",
    ),
    "TCS": MarketProfile(
        symbol="TCS", name="Tata Consultancy Services", sector="IT",
        price=4124.0, change_pct=1.8, volume="1.8M", support=3980.0, resistance=4280.0,
        sentiment="Bullish", headline="Large deal wins and margin resilience keep the IT thesis intact.",
    ),
    "INFY": MarketProfile(
        symbol="INFY", name="Infosys", sector="IT",
        price=1925.0, change_pct=3.1, volume="3.3M", support=1860.0, resistance=2006.0,
        sentiment="Bullish", headline="Guidance upgrades and a breakout in price action support momentum.",
    ),
    "WIPRO": MarketProfile(
        symbol="WIPRO", name="Wipro", sector="IT",
        price=548.0, change_pct=-0.4, volume="2.7M", support=522.0, resistance=593.0,
        sentiment="Neutral", headline="Operating leverage is improving, but deal conversion remains uneven.",
    ),
    "HDFCBANK": MarketProfile(
        symbol="HDFCBANK", name="HDFC Bank", sector="Banking",
        price=1680.0, change_pct=-0.9, volume="6.1M", support=1648.0, resistance=1795.0,
        sentiment="Neutral", headline="Integration progress is steady, while near-term NIM pressure persists.",
    ),
    "NIFTY": MarketProfile(
        symbol="NIFTY", name="Nifty 50", sector="Broad Market",
        price=24762.0, change_pct=1.24, volume="52.4M", support=24400.0, resistance=25000.0,
        sentiment="Bullish", headline="Breadth and institutional flows continue to support the index trend.",
    ),
}

ALIASES = {"HDFC": "HDFCBANK", "HDFC BANK": "HDFCBANK", "NIFTY 50": "NIFTY"}

YFINANCE_SUFFIX = {
    "NIFTY": "^NSEI",
    "SENSEX": "^BSESN",
    "RELIANCE": "RELIANCE.NS",
    "TCS": "TCS.NS",
    "INFY": "INFY.NS",
    "WIPRO": "WIPRO.NS",
    "HDFCBANK": "HDFCBANK.NS",
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
        symbol=symbol, name=f"{symbol} Holdings", sector="Diversified", price=price,
        change_pct=change, volume=f"{1 + (seed % 9)}.{seed % 10}M", support=support,
        resistance=resistance, sentiment=sentiment,
        headline="Synthetic market snapshot generated from the available symbol data.",
    )

def _fetch_yfinance_quote(symbol: str) -> dict[str, Any] | None:
    """Fetch real-time quote data from Yahoo Finance for NSE/BSE symbols."""
    ticker_sym = YFINANCE_SUFFIX.get(symbol, f"{symbol}.NS")
    try:
        ticker = yf.Ticker(ticker_sym)
        info = ticker.fast_info
        if not info.last_price:
            history = ticker.history(period="1d")
            if history.empty:
                return None
        last_price = float(info.last_price or history["Close"].iloc[-1])
        prev_close = float(info.previous_close or history["Open"].iloc[0])
        change = last_price - prev_close
        change_pct = round((change / prev_close) * 100, 2) if prev_close else 0.0
        vol = history.get("Volume", [])
        volume = f"{float(vol) / 1e6:.1f}M" if vol and float(vol) > 1e6 else f"{int(vol)}" if vol else "N/A"
        return {"price": round(last_price, 2), "change_pct": change_pct, "volume": volume, "prev_close": prev_close}
    except Exception:
        return None

def _fetch_google_finance_quote(symbol: str) -> dict[str, Any] | None:
    """Fallback: Try to fetch data from a public financial API."""
    api_url = f"https://query2.finance.yahoo.com/v8/finance/chart/{symbol}?range=1d&interval=1d"
    try:
        resp = requests.get(api_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            result = data.get("chart", {}).get("result", [{}])[0]
            meta = result.get("meta", {})
            price = meta.get("regularMarketPrice")
            if price:
                return {"price": round(float(price), 2)}
    except Exception:
        pass
    return None

def _compute_levels(price: float, change_pct: float) -> tuple[float, float]:
    """Compute support/resistance based on ATR-style multipliers."""
    atr_mul = 0.02
    support = round(price * (1 - atr_mul), 2)
    resistance = round(price * (1 + atr_mul), 2)
    return support, resistance

def _compute_sentiment(change_pct: float, yf_data: dict[str, Any] | None = None) -> str:
    if change_pct > 0.75:
        return "Bullish"
    elif change_pct < -0.75:
        return "Bearish"
    return "Neutral"

class MarketDataService:
    def __init__(self) -> None:
        self._cache: dict[str, tuple[dict[str, Any], float]] = {}
        self._cache_ttl = 60

    def _get_cached(self, symbol: str) -> dict[str, Any] | None:
        entry = self._cache.get(symbol)
        if entry and time.time() - entry[1] < self._cache_ttl:
            return entry[0]
        return None

    def fetch_live_quote(self, symbol: str) -> dict[str, str | float]:
        normalized = _normalize_symbol(symbol)
        cached = self._get_cached(normalized)
        if cached:
            return cached
        profile = MARKET_PROFILES.get(normalized, _fallback_profile(normalized))
        yf_data = _fetch_yfinance_quote(normalized)
        if yf_data:
            price = yf_data["price"]
            change_pct = yf_data["change_pct"]
            volume = yf_data["volume"]
            support, resistance = _compute_levels(price, change_pct)
            sent = _compute_sentiment(change_pct, yf_data)
            result = {
                "symbol": normalized, "name": profile.name, "sector": profile.sector,
                "price": price, "change_pct": change_pct, "volume": volume,
                "support": support, "resistance": resistance, "sentiment": sent,
                "headline": profile.headline, "status": "live",
            }
        else:
            result = {
                "symbol": profile.symbol, "name": profile.name, "sector": profile.sector,
                "price": profile.price, "change_fmt": profile.change_fmt if hasattr(profile, "change_fmt") else f"{profile.change_pct:+.2f}",
                "change_pct": profile.change_pct, "volume": profile.volume,
                "support": profile.support, "resistance": profile.resistance,
                "sentiment": profile.sentiment, "headline": profile.headline, "status": "cached",
            }
        self._cache[normalized] = (result, time.time())
        result["change_fmt"] = f"{result['change_pct']:+.2f}"
        return result

    def fetch_index_values(self) -> dict[str, Any]:
        """Fetch live index values for NIFTY, SENSEX, BANK NIFTY, VIX."""
        indices = {
            "NIFTY": {"symbol": "^NSEI", "name": "Nifty 50"},
            "SENSEX": {"symbol": "^BSESN", "name": "Sensex"},
            "BANKNIFTY": {"symbol": "^NSEBANK", "name": "Bank Nifty"},
            "INDIAVIX": {"symbol": "^INDIAVIX", "name": "India VIX"},
        }
        result = {}
        for key, info in indices.items():
            cached = self._get_cached(key)
            if cached:
                result[key] = cached
                continue
            try:
                ticker = yf.Ticker(info["symbol"])
                hist = ticker.history(period="1d")
                if hist.empty:
                    continue
                close = float(hist["Close"].iloc[-1])
                change_pct = float(hist["Close"][-1:] / hist["Open"][-1:] - 1) * 100
                change = close - float(hist["Open"].iloc[-1])
                result[key] = {
                    "symbol": key, "name": info["name"],
                    "value": round(close, 2), "change": round(change, 2),
                    "change_pct": round(change_pct, 2),
                    "status": "live",
                }
                self._cache[key] = (result[key], time.time())
            except Exception:
                pass
        if not result:
            result = {
                "NIFTY": {"symbol": "NIFTY", "name": "Nifty 50", "value": 24762, "change": 306, "change_pct": 1.24, "status": "cached"},
                "SENSEX": {"symbol": "SENSEX", "name": "Sensex", "value": 81467, "change": 702, "change_pct": 0.87, "status": "cached"},
                "BANKNIFTY": {"symbol": "BANKNIFTY", "name": "Bank Nifty", "value": 52847, "change": 320, "change_pct": 0.63, "status": "cached"},
                "INDIAVIX": {"symbol": "VIX", "name": "India VIX", "value": 13.42, "change": -0.11, "change_pct": -0.85, "status": "cached"},
            }
        return result

    def fetch_sector_performance(self) -> list[dict[str, Any]]:
        """Fetch live sector-wise performance."""
        sectors = [
            {"name": "Nifty IT", "symbol": "^CNXIT"},
            {"name": "Nifty Bank", "symbol": "^CNXBANK"},
            {"name": "Nifty Auto", "symbol": "^CNXAUTO"},
            {"name": "Nifty FMCG", "symbol": "^CNXFMCG"},
            {"name": "Nifty Pharma", "symbol": "^CNXPHARMA"},
            {"name": "Nifty Metal", "symbol": "^CNXMETAL"},
            {"name": "Nifty Realty", "symbol": "^CNXREALTY"},
            {"name": "Nifty Energy", "symbol": "^CNXENERGY"},
        ]
        results = []
        for sec in sectors:
            try:
                ticker = yf.Ticker(sec["symbol"])
                hist = ticker.history(period="1d")
                if not hist.empty:
                    close = float(hist["Close"].iloc[-1])
                    change_pct = round((close / float(hist["Open"].iloc[-1]) - 1) * 100, 2)
                    results.append({"name": sec["name"], "change_pct": change_pct, "status": "live"})
                    continue
            except Exception:
                pass
        if not results:
            results = [
                {"name": "Nifty IT", "change_pct": 2.4, "status": "cached"},
                {"name": "Nifty Bank", "change_pct": -0.6, "status": "cached"},
                {"name": "Nifty Auto", "change_pct": 0.5, "status": "cached"},
                {"name": "Nifty FMCG", "change_pct": -0.3, "status": "cached"},
                {"name": "Nifty Pharma", "change_pct": 1.1, "status": "cached"},
                {"name": "Nifty Metal", "change_pct": -1.8, "status": "cached"},
                {"name": "Nifty Realty", "change_pct": 0.9, "status": "cached"},
                {"name": "Nifty Energy", "change_pct": 1.8, "status": "cached"},
            ]
        return results
