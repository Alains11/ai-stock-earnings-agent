# Fortune 500 Monthly Earnings Agent

This agent fetches monthly earnings releases, matches them to the companies in
`data/fortune500.csv`, calculates EPS and revenue beats versus consensus, and
writes a Markdown digest with sector breakdowns.

## Setup

Install the project's Python dependencies, then set a Finnhub API key:

```sh
export FINNHUB_API_KEY="your-key"
```

Replace the starter CSV with the current Fortune 500 list. It must contain
`ticker`, `company`, and `sector` columns.

## Run a monthly digest

The default is the previous completed calendar month:

```sh
cd /path/to/ai-earnings-reporter-agent
python app.py --monthly --output reports/latest.md
```

To backfill a specific month:

```sh
python app.py --monthly --month 2026-08 --output reports/2026-08.md
```

Schedule the command with cron, GitHub Actions, or another job scheduler on the
first day of each month. Finnhub is the source for actual and consensus
earnings values; missing API data is reported as an empty digest rather than
fabricated.
