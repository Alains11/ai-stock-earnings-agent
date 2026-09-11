from __future__ import annotations

import logging
from typing import Any, Dict, List

import requests

try:
    from .config import get_market_data_config
except ImportError:
    from config import get_market_data_config

logger = logging.getLogger(__name__)


def fetch_earnings_calendar(from_date: str, to_date: str) -> List[Dict[str, Any]]:
    """Fetch all earnings releases between from_date and to_date (YYYY-MM-DD).

    Each entry (when Finnhub has data) includes symbol, date, quarter, year,
    epsActual, epsEstimate, revenueActual, revenueEstimate -- this is the
    only genuinely real, cross-company comparable data source in this
    pipeline, and is what the monthly digest's beat/miss analysis relies on.

    Requires FINNHUB_API_KEY. Returns an empty list (and logs a warning) if
    no key is configured or the request fails, so a scheduled/unattended run
    never crashes outright on a data-provider outage.
    """
    api_key = get_market_data_config()["finnhub_api_key"]
    if not api_key:
        logger.warning("FINNHUB_API_KEY not set; cannot fetch earnings calendar.")
        return []
    try:
        response = requests.get(
            "https://finnhub.io/api/v1/calendar/earnings",
            params={"from": from_date, "to": to_date, "token": api_key},
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        return data.get("earningsCalendar", [])
    except Exception:
        logger.exception("Failed to fetch earnings calendar for %s to %s", from_date, to_date)
        return []
