from __future__ import annotations

import calendar
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    from .digest_generator import build_markdown_digest
    from .earnings_calendar import fetch_earnings_calendar
    from .fortune500 import load_fortune500
    from .llm_client import generate_narrative
    from .sector_analytics import build_digest_records, compute_beat_rates, sector_breakdown
except ImportError:
    from digest_generator import build_markdown_digest
    from earnings_calendar import fetch_earnings_calendar
    from fortune500 import load_fortune500
    from llm_client import generate_narrative
    from sector_analytics import build_digest_records, compute_beat_rates, sector_breakdown


def _month_range(month: Optional[str] = None) -> Tuple[date, date]:
    """Return the inclusive UTC date range for a YYYY-MM month."""
    if month:
        try:
            first = datetime.strptime(month, "%Y-%m").date().replace(day=1)
        except ValueError as exc:
            raise ValueError("month must use YYYY-MM format") from exc
    else:
        today = date.today()
        first = today.replace(day=1) - timedelta(days=1)
        first = first.replace(day=1)
    last = first.replace(day=calendar.monthrange(first.year, first.month)[1])
    return first, last


def _build_narrative(month_label: str, beat_rates: Dict[str, Any]) -> Optional[str]:
    prompt = (
        f"Write a concise, factual executive summary for the Fortune 500 earnings "
        f"digest for {month_label}. {beat_rates['companies_reporting']} companies "
        f"reported; EPS beat rate was {beat_rates['eps_beat_rate_pct']}% and "
        f"revenue beat rate was {beat_rates['revenue_beat_rate_pct']}%. "
        "Do not invent company-specific facts or guidance. State when data is unavailable."
    )
    return generate_narrative(prompt)


def run_monthly_digest(
    month: Optional[str] = None,
    fortune500_path: Optional[Path] = None,
    include_narrative: bool = False,
) -> str:
    """Fetch one month's Fortune 500 earnings and return a Markdown digest."""
    start, end = _month_range(month)
    companies = load_fortune500(fortune500_path)
    lookup = {company["ticker"]: company for company in companies}
    entries = fetch_earnings_calendar(start.isoformat(), end.isoformat())
    records = build_digest_records(entries, lookup)
    beat_rates = compute_beat_rates(records)
    narrative = _build_narrative(start.strftime("%B %Y"), beat_rates) if include_narrative else None
    return build_markdown_digest(
        start.strftime("%B %Y"),
        records,
        beat_rates,
        sector_breakdown(records),
        narrative=narrative,
    )
