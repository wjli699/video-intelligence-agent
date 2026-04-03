"""Event helpers and constants for the skill layer."""

from __future__ import annotations

from typing import Any

from core.schema import NormalizedEvent


def dict_to_normalized(d: dict[str, Any], include_raw: bool = False) -> NormalizedEvent:
    payload = {k: d.get(k) for k in ("camera", "label", "start_time", "end_time", "confidence")}
    if include_raw:
        payload["raw"] = d
    return NormalizedEvent.model_validate(payload)
