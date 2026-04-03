from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from pydantic import BaseModel, Field


class NormalizedEvent(BaseModel):
    """Canonical event shape after adapter normalization (schema v0)."""

    camera: Optional[str] = None
    label: Optional[str] = None
    start_time: Optional[float] = Field(
        default=None,
        description="Unix timestamp from source (e.g. Frigate after.start_time)",
    )
    end_time: Optional[float] = None
    confidence: Optional[float] = None
    raw: Optional[dict[str, Any]] = Field(
        default=None,
        description="Optional original payload subset for debugging",
    )

    def to_db_row(self) -> dict[str, Any]:
        """Map to DB columns (timestamps as datetime)."""
        return {
            "camera": self.camera,
            "label": self.label,
            "start_time": _unix_to_dt(self.start_time),
            "end_time": _unix_to_dt(self.end_time),
            "confidence": self.confidence,
        }


def _unix_to_dt(ts: Optional[float]) -> Optional[datetime]:
    if ts is None:
        return None
    return datetime.fromtimestamp(float(ts), tz=timezone.utc).replace(tzinfo=None)
