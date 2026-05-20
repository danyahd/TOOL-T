import requests
import streamlit as st

COINGECKO_BASE = "https://api.coingecko.com/api/v3"


def _headers() -> dict:
    try:
        key = st.secrets.get("COINGECKO_API_KEY", "")
        return {"x-cg-demo-api-key": key} if key else {}
    except Exception:
        return {}

COINS = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "BNB": "binancecoin",
    "SOL": "solana",
    "XRP": "ripple",
    "AVAX": "avalanche-2",
    "LINK": "chainlink",
    "ADA": "cardano",
    # Layer 2s
    "MATIC": "polygon-ecosystem-token",
    "ARB": "arbitrum",
    "OP": "optimism",
}

# Volume thresholds (USD) to classify strength per coin
VOLUME_THRESHOLDS = {
    "BTC": (50e9, 20e9),
    "ETH": (20e9, 8e9),
    "BNB": (1e9, 400e6),
    "SOL": (3e9, 1e9),
    "XRP": (3e9, 1e9),
    "AVAX": (500e6, 200e6),
    "LINK": (500e6, 150e6),
    "ADA": (500e6, 200e6),
    "MATIC": (400e6, 150e6),
    "ARB": (300e6, 100e6),
    "OP": (200e6, 80e6),
}


def get_prices() -> dict:
    ids = ",".join(COINS.values())
    try:
        r = requests.get(
            f"{COINGECKO_BASE}/simple/price",
            params={
                "ids": ids,
                "vs_currencies": "usd",
                "include_24hr_change": "true",
                "include_24hr_vol": "true",
            },
            headers=_headers(),
            timeout=10,
        )
        r.raise_for_status()
        return r.json()
    except Exception:
        return {}


def get_ohlc(coin_id: str, days: int = 7) -> list:
    try:
        r = requests.get(
            f"{COINGECKO_BASE}/coins/{coin_id}/ohlc",
            params={"vs_currency": "usd", "days": days},
            headers=_headers(),
            timeout=10,
        )
        r.raise_for_status()
        return r.json()
    except Exception:
        return []


def classify_trend(change_24h: float) -> tuple[str, str]:
    if change_24h >= 3:
        return "Uptrend", "✅"
    elif change_24h <= -3:
        return "Downtrend", "🔴"
    return "Sideways", "⚠️"


def classify_volume(vol_24h: float, symbol: str) -> str:
    high, low = VOLUME_THRESHOLDS.get(symbol, (1e9, 400e6))
    if vol_24h >= high:
        return "High 🔥"
    elif vol_24h >= low:
        return "Normal"
    return "Low 📉"


def get_support_resistance(ohlc: list) -> tuple[float | None, float | None]:
    if not ohlc:
        return None, None
    highs = [c[2] for c in ohlc]
    lows = [c[3] for c in ohlc]
    return min(lows), max(highs)
