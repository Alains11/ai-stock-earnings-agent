from __future__ import annotations

import logging
from typing import Optional

import requests

try:
    from .config import get_model_config
except ImportError:
    from config import get_model_config

logger = logging.getLogger(__name__)


def generate_narrative(prompt: str, timeout: int = 60) -> Optional[str]:
    """Ask the configured local Ollama model for a short narrative paragraph.

    Returns None (never raises) if Ollama is unreachable, misconfigured, or
    a non-Ollama provider is set -- narrative generation is always an
    optional enhancement layered on top of the deterministic numbers, never
    a hard dependency for producing a report.
    """
    config = get_model_config()
    if config["provider"] != "ollama":
        logger.info("LLM_PROVIDER is not 'ollama' (got %r); skipping narrative generation.", config["provider"])
        return None
    try:
        response = requests.post(
            f"{config['base_url']}/api/chat",
            json={
                "model": config["model_name"],
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
            },
            timeout=timeout,
        )
        response.raise_for_status()
        data = response.json()
        content = data.get("message", {}).get("content")
        return content.strip() if content else None
    except Exception:
        logger.exception("Ollama narrative generation failed; continuing without it.")
        return None
