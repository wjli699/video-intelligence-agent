from __future__ import annotations

import asyncio
from typing import Any

from llm.client import summarize_events

from plugins.base import AgentPlugin


class SimplePlugin(AgentPlugin):
    """Default plugin: same behavior as the previous direct `summarize_events` call."""

    async def summarize(self, events: list[dict[str, Any]]) -> dict[str, Any]:
        return await asyncio.to_thread(summarize_events, events)
