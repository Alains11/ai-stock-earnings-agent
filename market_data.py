from __future__ import annotations

from typing import Any, Dict

import requests

try:
    from .config import get_market_data_config
except ImportError:
    from config import get_market_data_config


def fetch_realtime_quote(ticker: str) -> Dict[str, Any]:
    """Fetch a real-time (or best-available) quote for the given ticker.

    Uses Finnhub if FINNHUB_API_KEY is set (true real-time for US equities
    on the free tier). Falls back to Yahoo Finance via yfinance (typically
    ~15 min delayed) when no key is present or the Finnhub call fails.
    """
    config = get_market_data_config()
    api_key = config["finnhub_api_key"]
    if api_key:
        try:
            return _fetch_finnhub_quote(ticker, api_key)
        except Exception:
            pass
    return _fetch_yfinance_quote(ticker)


def _fetch_finnhub_quote(ticker: str, api_key: str) -> Dict[str, Any]:
    response = requests.get(
        "https://finnhub.io/api/v1/quote",
        params={"symbol": ticker.upper(), "token": api_key},
        timeout=10,
    )
    response.raise_for_status()
    data = response.json()
    if not data or not data.get("c"):
        raise ValueError("Finnhub returned no quote data")
    return {
        "ticker": ticker.upper(),
        "price": data.get("c"),
        "change": data.get("d"),
        "change_pct": data.get("dp"),
        "high": data.get("h"),
        "low": data.get("l"),
        "open": data.get("o"),
        "prev_close": data.get("pc"),
        "source": "Finnhub (real-time)",
    }


def _fetch_yfinance_quote(ticker: str) -> Dict[str, Any]:
    import yfinance as yf

    stock = yf.Ticker(ticker.upper())
    info = stock.fast_info
    return {
        "ticker": ticker.upper(),
        "price": info.get("last_price"),
        "change": None,
        "change_pct": None,
        "high": info.get("day_high"),
        "low": info.get("day_low"),
        "open": info.get("open"),
        "prev_close": info.get("previous_close"),
        "source": "Yahoo Finance via yfinance (delayed ~15 min, no key required)",
    }
