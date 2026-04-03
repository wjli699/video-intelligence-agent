from __future__ import annotations

from typing import Any

from adapters.base import VMSAdapter


class FrigateAdapter(VMSAdapter):
    """Normalize Frigate MQTT `frigate/events` payloads."""

    def ingest_event(self, raw_event: dict[str, Any]) -> dict[str, Any]:
        after = raw_event.get("after") or {}
        event = {
            "camera": after.get("camera"),
            "label": after.get("label"),
            "start_time": after.get("start_time"),
            "end_time": after.get("end_time"),
            "confidence": after.get("top_score"),
        }
        return event
