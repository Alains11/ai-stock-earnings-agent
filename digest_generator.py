from __future__ import annotations

from typing import Any, Dict, List, Optional

try:
    from .sector_analytics import notable_misses, top_outperformers
except ImportError:
    from sector_analytics import notable_misses, top_outperformers


def _fmt_pct(value: Optional[float]) -> str:
    return "N/A" if value is None else f"{value:+.2f}%"


def _fmt_num(value: Optional[float]) -> str:
    return "N/A" if value is None else f"{value:,.2f}"


def _fmt_money(value: Optional[float]) -> str:
    return "N/A" if value is None else f"${value:,.0f}"


def build_markdown_digest(
    month_label: str,
    records: List[Dict[str, Any]],
    beat_rates: Dict[str, Any],
    sector_data: Dict[str, Dict[str, Any]],
    narrative: Optional[str] = None,
) -> str:
    lines: List[str] = []
    lines.append(f"# Fortune 500 Earnings Digest — {month_label}")
    lines.append("")
    lines.append("### Data Integrity Notice")
    lines.append(
        "- Beat/miss figures below come from consensus estimates reported via "
        "Finnhub's earnings calendar (actual vs. estimate at time of release) "
        "for companies matched against `data/fortune500.csv`."
    )
    lines.append(
        "- This digest does **not** include year-over-year revenue/EPS growth "
        "trends. The per-company deep-dive report in this project still uses "
        "a single placeholder demo dataset rather than live filing figures, "
        "so YoY comparisons would be identical (fabricated) across every "
        "company if included here. That gap needs live SEC/XBRL financials "
        "wired in before trend claims can be trusted at this scale."
    )
    lines.append(
        "- \"Guidance revisions\" narrative has no deterministic data source "
        "in this pipeline. Where an AI-drafted summary appears below, it is "
        "explicitly labeled unverified and should be reviewed before "
        "distribution."
    )
    lines.append("")

    lines.append("## Executive Summary")
    lines.append(f"- Fortune 500 companies reporting this period: **{beat_rates['companies_reporting']}**")
    lines.append(
        f"- EPS beat rate: **{_fmt_pct(beat_rates['eps_beat_rate_pct'])}** "
        f"of {beat_rates['companies_with_eps_estimate']} companies with a consensus estimate"
    )
    lines.append(
        f"- Revenue beat rate: **{_fmt_pct(beat_rates['revenue_beat_rate_pct'])}** "
        f"of {beat_rates['companies_with_revenue_estimate']} companies with a consensus estimate"
    )
    lines.append(f"- Average EPS surprise vs. consensus: **{_fmt_pct(beat_rates['avg_eps_surprise_pct'])}**")
    lines.append(f"- Average revenue surprise vs. consensus: **{_fmt_pct(beat_rates['avg_revenue_surprise_pct'])}**")
    if narrative:
        lines.append("")
        lines.append("**AI-drafted narrative (unverified, local Ollama model — review before distribution):**")
        lines.append("")
        lines.append(narrative)
    lines.append("")

    lines.append("## Key Highlights & Outperformers")
    lines.append("Top 5 EPS beats vs. consensus estimate:")
    lines.append("")
    lines.append("| Ticker | Company | Sector | EPS Actual | EPS Est. | Surprise |")
    lines.append("|---|---|---|---:|---:|---:|")
    top5 = top_outperformers(records, "eps_surprise_pct", 5)
    if top5:
        for r in top5:
            lines.append(
                f"| {r['ticker']} | {r['company']} | {r['sector']} | "
                f"{_fmt_num(r['eps_actual'])} | {_fmt_num(r['eps_estimate'])} | {_fmt_pct(r['eps_surprise_pct'])} |"
            )
    else:
        lines.append("| — | No companies with both actual and estimate EPS this period | | | | |")
    lines.append("")

    lines.append("## Notable Misses & Guidance Revisions")
    misses = notable_misses(records, "eps_surprise_pct", 0.0)
    if misses:
        lines.append("Companies missing EPS consensus:")
        lines.append("")
        lines.append("| Ticker | Company | Sector | EPS Actual | EPS Est. | Surprise |")
        lines.append("|---|---|---|---:|---:|---:|")
        for r in misses:
            lines.append(
                f"| {r['ticker']} | {r['company']} | {r['sector']} | "
                f"{_fmt_num(r['eps_actual'])} | {_fmt_num(r['eps_estimate'])} | {_fmt_pct(r['eps_surprise_pct'])} |"
            )
    else:
        lines.append("No EPS misses detected among companies with a consensus estimate this period.")
    lines.append("")
    lines.append(
        "Guidance revisions: `Unverified / Needs Manual Review` — no deterministic "
        "data source is wired into this pipeline for forward-guidance language."
    )
    lines.append("")

    lines.append("## Sector-by-Sector Breakdown")
    lines.append("| Sector | Companies | EPS Beat Rate | Revenue Beat Rate | Avg EPS Surprise |")
    lines.append("|---|---:|---:|---:|---:|")
    for sector in sorted(sector_data.keys()):
        stats = sector_data[sector]
        lines.append(
            f"| {sector} | {stats['company_count']} | {_fmt_pct(stats['eps_beat_rate_pct'])} | "
            f"{_fmt_pct(stats['revenue_beat_rate_pct'])} | {_fmt_pct(stats['avg_eps_surprise_pct'])} |"
        )
    lines.append("")

    lines.append("## Detailed Earnings Table")
    lines.append(
        "| Ticker | Company | Sector | Report Date | EPS Actual | EPS Est. | "
        "EPS Surprise | Revenue Actual | Revenue Est. | Revenue Surprise |"
    )
    lines.append("|---|---|---|---|---:|---:|---:|---:|---:|---:|")
    for r in sorted(records, key=lambda x: x["ticker"]):
        lines.append(
            f"| {r['ticker']} | {r['company']} | {r['sector']} | {r.get('date', 'N/A')} | "
            f"{_fmt_num(r['eps_actual'])} | {_fmt_num(r['eps_estimate'])} | {_fmt_pct(r['eps_surprise_pct'])} | "
            f"{_fmt_money(r['revenue_actual'])} | {_fmt_money(r['revenue_estimate'])} | {_fmt_pct(r['revenue_surprise_pct'])} |"
        )
    lines.append("")
    lines.append("---")
    lines.append("Source: Finnhub earnings calendar API, cross-referenced against `data/fortune500.csv`")
    return "\n".join(lines)
