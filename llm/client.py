from __future__ import annotations

import os
from typing import Any

import requests
from dotenv import load_dotenv

load_dotenv()

DEFAULT_LLM_URL = os.getenv("LLM_BASE_URL", "http://127.0.0.1:8000")


def summarize_events(events: list[dict[str, Any]], *, base_url: str | None = None) -> dict[str, Any]:
    """
    Call remote llama.cpp-compatible `/completion` (or similar) HTTP endpoint.
    Set LLM_BASE_URL to the Local PC or Jetson running the LLM, e.g. http://192.168.1.50:8000
    """
    url = (base_url or DEFAULT_LLM_URL).rstrip("/") + "/completion"
    prompt = (
        "Summarize the following video analytics events in 2-4 short bullet points. "
        "Focus on notable activity, time patterns, and cameras.\n\n"
        f"Events: {events!r}"
    )
    res = requests.post(url, json={"prompt": prompt}, timeout=120)
    res.raise_for_status()
    return res.json()
