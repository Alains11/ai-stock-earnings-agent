from __future__ import annotations

from typing import Any, Dict, TypedDict

from langgraph.graph import END, StateGraph

from .financial_math import build_verification_log, validate_metrics
from .market_data import fetch_realtime_quote


class EarningsState(TypedDict, total=False):
    ticker: str
    filing_type: str
    period: str
    query: str
    research_plan: Dict[str, Any]
    filing_metadata: Dict[str, Any]
    market_quote: Dict[str, Any]
    validated_metrics: Dict[str, Any]
    audit_log: list
    markdown_report: str
    status: str


def parse_query(state: EarningsState) -> EarningsState:
    ticker = (state.get("ticker") or "AAPL").upper()
    filing_type = (state.get("filing_type") or "10-Q").upper()
    period = (state.get("period") or "Q2-2026").upper()
    return {
        **state,
        "ticker": ticker,
        "filing_type": filing_type,
        "period": period,
        "query": f"{ticker} {period} {filing_type}",
    }


def lead_research_agent(state: EarningsState) -> EarningsState:
    research_plan = {
        "primary_objectives": [
            "Revenue and EPS trend analysis",
            "GAAP versus non-GAAP context",
            "Operational risk and legal exposures",
            "Forward-looking statements review"
        ],
        "questions": [
            "What changed sequentially and year-over-year?",
            "Which margins and ratios are most material?",
            "Which statements require manual review due to ambiguity?"
        ],
        "focus": f"{state['ticker']} {state['period']} {state['filing_type']}"
    }
    return {**state, "research_plan": research_plan}


def retrieval_agent(state: EarningsState) -> EarningsState:
    filing_metadata = fetch_filing_metrics(state["ticker"], state["filing_type"], state["period"])
    return {**state, "filing_metadata": filing_metadata}


def market_data_agent(state: EarningsState) -> EarningsState:
    quote = fetch_realtime_quote(state["ticker"])
    return {**state, "market_quote": quote}


def fact_check_agent(state: EarningsState) -> EarningsState:
    metrics = state["filing_metadata"]["metrics"]
    validated = validate_metrics(metrics)
    source_url = state["filing_metadata"].get("source", "https://www.sec.gov/")
    audit_log = build_verification_log(validated, source_url)
    return {**state, "validated_metrics": validated, "audit_log": audit_log}


def report_agent(state: EarningsState) -> EarningsState:
    report = build_markdown_report(state)
    return {**state, "markdown_report": report, "status": "completed"}


def build_graph():
    workflow = StateGraph(EarningsState)
    workflow.add_node("parse_query", parse_query)
    workflow.add_node("research_agent", lead_research_agent)
    workflow.add_node("retrieval_agent", retrieval_agent)
    workflow.add_node("market_data_agent", market_data_agent)
    workflow.add_node("fact_check_agent", fact_check_agent)
    workflow.add_node("report_agent", report_agent)

    workflow.set_entry_point("parse_query")
    workflow.add_edge("parse_query", "research_agent")
    workflow.add_edge("research_agent", "retrieval_agent")
    workflow.add_edge("retrieval_agent", "market_data_agent")
    workflow.add_edge("market_data_agent", "fact_check_agent")
    workflow.add_edge("fact_check_agent", "report_agent")
    workflow.add_edge("report_agent", END)
    return workflow.compile()


def run_workflow(payload: Dict[str, Any]) -> str:
    graph = build_graph()
    result = graph.invoke({
        "ticker": payload.get("ticker", "AAPL"),
        "filing_type": payload.get("filing_type", "10-Q"),
        "period": payload.get("period", "Q2-2026"),
    })
    return result["markdown_report"]
