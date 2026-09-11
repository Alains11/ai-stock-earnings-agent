from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from .monthly_digest import run_monthly_digest
except ImportError:
    from monthly_digest import run_monthly_digest


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the financial earnings briefing workflow.")
    parser.add_argument("--input", help="Path to the input JSON file for a single-company report")
    parser.add_argument("--output", required=True, help="Path to the output Markdown report")
    parser.add_argument(
        "--monthly",
        action="store_true",
        help="Fetch and write the previous calendar month's Fortune 500 digest",
    )
    parser.add_argument(
        "--month",
        help="Month to fetch in YYYY-MM format (defaults to the previous calendar month)",
    )
    parser.add_argument(
        "--fortune500",
        type=Path,
        help="Path to a Fortune 500 CSV (ticker,company,sector)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if args.monthly:
        if args.input:
            raise SystemExit("--input cannot be combined with --monthly")
        report = run_monthly_digest(month=args.month, fortune500_path=args.fortune500)
    else:
        if not args.input:
            raise SystemExit("--input is required unless --monthly is used")
        try:
            from .workflow import run_workflow
        except ImportError:
            from workflow import run_workflow
        input_path = Path(args.input)
        with input_path.open("r", encoding="utf-8") as fh:
            payload = json.load(fh)
        report = run_workflow(payload)
    output_path.write_text(report, encoding="utf-8")

    print(f"Report written to {output_path}")


if __name__ == "__main__":
    main()
