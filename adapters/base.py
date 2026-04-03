from __future__ import annotations

from typing import Any


class VMSAdapter:
    """Generic VMS / NVR event adapter. Implement per vendor (Frigate first)."""

    def ingest_event(self, raw_event: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError
