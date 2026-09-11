from __future__ import annotations

from typing import Any, Dict, List, Optional


def _pct_surprise(actual: Optional[float], estimate: Optional[float]) -> Optional[float]:
    if actual is None or estimate in (None, 0):
        return None
    return ((actual - estimate) / abs(estimate)) * 100.0


def build_digest_records(
    calendar_entries: List[Dict[str, Any]],
    fortune_lookup: Dict[str, Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Join Finnhub earnings calendar entries against the Fortune 500 list.

    Only entries whose ticker is present in fortune_lookup are kept. Each
    output record carries the raw actual/estimate figures plus a computed
    surprise percentage for both EPS and revenue.
    """
    records: List[Dict[str, Any]] = []
    for entry in calendar_entries:
        ticker = str(entry.get("symbol", "")).upper()
        info = fortune_lookup.get(ticker)
        if not info:
            continue
        eps_actual = entry.get("epsActual")
        eps_estimate = entry.get("epsEstimate")
        rev_actual = entry.get("revenueActual")
        rev_estimate = entry.get("revenueEstimate")
        records.append(
            {
                "ticker": ticker,
                "company": info.get("company", ticker),
                "sector": info.get("sector", "Unclassified"),
                "date": entry.get("date"),
                "quarter": entry.get("quarter"),
                "year": entry.get("year"),
                "eps_actual": eps_actual,
                "eps_estimate": eps_estimate,
                "eps_surprise_pct": _pct_surprise(eps_actual, eps_estimate),
                "revenue_actual": rev_actual,
                "revenue_estimate": rev_estimate,
                "revenue_surprise_pct": _pct_surprise(rev_actual, rev_estimate),
            }
        )
    return records


def _has_both(record: Dict[str, Any], key: str) -> bool:
    return record.get(f"{key}_actual") is not None and record.get(f"{key}_estimate") is not None


def compute_beat_rates(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    eps_scored = [r for r in records if _has_both(r, "eps")]
    rev_scored = [r for r in records if _has_both(r, "revenue")]
    eps_beats = [r for r in eps_scored if r["eps_actual"] > r["eps_estimate"]]
    rev_beats = [r for r in rev_scored if r["revenue_actual"] > r["revenue_estimate"]]
    avg_eps_surprise = (
        sum(r["eps_surprise_pct"] for r in eps_scored) / len(eps_scored) if eps_scored else None
    )
    avg_rev_surprise = (
        sum(r["revenue_surprise_pct"] for r in rev_scored) / len(rev_scored) if rev_scored else None
    )
    return {
        "companies_reporting": len(records),
        "companies_with_eps_estimate": len(eps_scored),
        "companies_with_revenue_estimate": len(rev_scored),
        "eps_beat_rate_pct": (len(eps_beats) / len(eps_scored) * 100.0) if eps_scored else None,
        "revenue_beat_rate_pct": (len(rev_beats) / len(rev_scored) * 100.0) if rev_scored else None,
        "avg_eps_surprise_pct": avg_eps_surprise,
        "avg_revenue_surprise_pct": avg_rev_surprise,
    }


def top_outperformers(records: List[Dict[str, Any]], key: str = "eps_surprise_pct", n: int = 5) -> List[Dict[str, Any]]:
    scored = [r for r in records if r.get(key) is not None]
    return sorted(scored, key=lambda r: r[key], reverse=True)[:n]


def notable_misses(records: List[Dict[str, Any]], key: str = "eps_surprise_pct", threshold: float = 0.0) -> List[Dict[str, Any]]:
    scored = [r for r in records if r.get(key) is not None]
    return sorted([r for r in scored if r[key] < threshold], key=lambda r: r[key])


def sector_breakdown(records: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    sectors: Dict[str, List[Dict[str, Any]]] = {}
    for r in records:
        sectors.setdefault(r["sector"], []).append(r)
    breakdown: Dict[str, Dict[str, Any]] = {}
    for sector, items in sectors.items():
        stats = compute_beat_rates(items)
        stats["company_count"] = len(items)
        breakdown[sector] = stats
    return breakdown
