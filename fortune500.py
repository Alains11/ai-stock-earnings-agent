from __future__ import annotations

import csv
from pathlib import Path
from typing import Any, Dict, List, Optional

DEFAULT_PATH = Path(__file__).resolve().parent / "data" / "fortune500.csv"


def load_fortune500(path: Optional[Path] = None) -> List[Dict[str, Any]]:
    """Load the Fortune 500 ticker/company/sector list from data/fortune500.csv.

    NOTE: This repo ships only a small starter sample. Replace
    data/fortune500.csv with the full current-year list (ticker,company,sector
    columns) sourced from Fortune's official ranking before relying on this
    for production monthly runs.
    """
    csv_path = path or DEFAULT_PATH
    if not csv_path.exists():
        raise FileNotFoundError(
            f"Fortune 500 ticker list not found at {csv_path}. "
            "Create data/fortune500.csv with 'ticker,company,sector' columns."
        )
    with csv_path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.DictReader(fh)
        return [
            {
                "ticker": row["ticker"].strip().upper(),
                "company": row["company"].strip(),
                "sector": (row.get("sector") or "Unclassified").strip() or "Unclassified",
            }
            for row in reader
            if row.get("ticker")
        ]


def fortune500_lookup(path: Optional[Path] = None) -> Dict[str, Dict[str, Any]]:
    """Same data as load_fortune500, keyed by ticker for O(1) lookups."""
    return {row["ticker"]: row for row in load_fortune500(path)}
