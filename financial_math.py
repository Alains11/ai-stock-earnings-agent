from __future__ import annotations

import math
from typing import Any, Dict, List, Optional

import duckdb
import pandas as pd


def pct_change(current: float, previous: float) -> Optional[float]:
    if previous in (None, 0) or current is None:
        return None
    return ((current - previous) / abs(previous)) * 100.0


def _safe_float(value: Any) -> Optional[float]:
    if value is None:
        return None
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return None if math.isnan(result) else result


def validate_metrics(metrics: Dict[str, Any]) -> Dict[str, Any]:
    revenue = metrics["revenue"]
    net_income = metrics["net_income"]
    eps = metrics["eps"]

    frame = pd.DataFrame(
        [
            {"metric": "revenue", "current": revenue["current"], "prev": revenue["prev"], "year_ago": revenue["year_ago"]},
            {"metric": "net_income", "current": net_income["current"], "prev": net_income["prev"], "year_ago": net_income["year_ago"]},
            {"metric": "eps", "current": eps["current"], "prev": eps["prev"], "year_ago": eps["year_ago"]},
        ]
    )

    sql = """
        SELECT
            metric,
            100.0 * (current - prev) / NULLIF(ABS(prev), 0) AS qoq_pct,
            100.0 * (current - year_ago) / NULLIF(ABS(year_ago), 0) AS yoy_pct
        FROM frame
    """
    result = duckdb.query(sql).df()
    result = result.set_index("metric")

    verified = {
        "revenue_qoq_pct": _safe_float(result.loc["revenue", "qoq_pct"]),
        "revenue_yoy_pct": _safe_float(result.loc["revenue", "yoy_pct"]),
        "net_income_qoq_pct": _safe_float(result.loc["net_income", "qoq_pct"]),
        "net_income_yoy_pct": _safe_float(result.loc["net_income", "yoy_pct"]),
        "eps_qoq_pct": _safe_float(result.loc["eps", "qoq_pct"]),
        "eps_yoy_pct": _safe_float(result.loc["eps", "yoy_pct"]),
        "gross_margin_pct": _safe_float(metrics.get("gross_margin_pct")),
        "operating_margin_pct": _safe_float(metrics.get("operating_margin_pct")),
    }

    return verified


def _fmt_pct(value: Optional[float]) -> str:
    return "N/A" if value is None else f"{value:.2f}%"


def build_verification_log(facts: Dict[str, Any], source_url: str) -> List[Dict[str, Any]]:
    audit_rows = [
        {
            "fact": "Revenue QoQ growth",
            "value": _fmt_pct(facts["revenue_qoq_pct"]),
            "source": source_url,
            "verification": "Verified via deterministic Python + duckdb calculation",
            "confidence": "High" if facts["revenue_qoq_pct"] is not None else "N/A",
        },
        {
            "fact": "Revenue YoY growth",
            "value": _fmt_pct(facts["revenue_yoy_pct"]),
            "source": source_url,
            "verification": "Verified via deterministic Python + duckdb calculation",
            "confidence": "High" if facts["revenue_yoy_pct"] is not None else "N/A",
        },
        {
            "fact": "EPS YoY growth",
            "value": _fmt_pct(facts["eps_yoy_pct"]),
            "source": source_url,
            "verification": "Verified via deterministic Python + duckdb calculation",
            "confidence": "High" if facts["eps_yoy_pct"] is not None else "N/A",
        },
        {
            "fact": "Risk highlight summary",
            "value": "Unverified / Needs Manual Review",
            "source": source_url,
            "verification": "Narrative summary not numerically validated",
            "confidence": "Medium",
        },
    ]
    return audit_rows
