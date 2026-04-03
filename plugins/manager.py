from __future__ import annotations

import os
from typing import Callable

from dotenv import load_dotenv

from plugins.base import AgentPlugin
from plugins.simple_plugin import SimplePlugin

load_dotenv()

PluginFactory = Callable[[], AgentPlugin]

_REGISTRY: dict[str, PluginFactory] = {
    "simple": SimplePlugin,
}

_plugin: AgentPlugin | None = None


def load_plugin() -> AgentPlugin:
    """Instantiate the plugin named by env `PLUGIN` (default: simple)."""
    name = os.getenv("PLUGIN", "simple").strip().lower()
    factory = _REGISTRY.get(name)
    if factory is None:
        known = ", ".join(sorted(_REGISTRY))
        raise ValueError(f"Unknown PLUGIN={name!r}. Choose one of: {known}")
    return factory()


def get_plugin() -> AgentPlugin:
    """Singleton plugin instance for the process."""
    global _plugin
    if _plugin is None:
        _plugin = load_plugin()
    return _plugin
