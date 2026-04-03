from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class AgentPlugin(ABC):
    @abstractmethod
    async def summarize(self, events: list[dict[str, Any]]) -> dict[str, Any]:
        """Produce a summary payload from recent events (e.g. LLM JSON)."""
