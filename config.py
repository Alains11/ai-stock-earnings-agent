from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")


def get_model_config() -> dict:
    provider = os.getenv("LLM_PROVIDER", "ollama").lower()
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
    return {
        "provider": provider,
        "model_name": os.getenv("MODEL_NAME", "llama3.2-16k:latest"),
        "base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        "api_key": api_key,
        "user_agent": os.getenv("SEC_USER_AGENT", "CopilotResearchAgent contact@example.com"),
    }


def get_market_data_config() -> dict:
    return {
        "finnhub_api_key": os.getenv("FINNHUB_API_KEY"),
    }
