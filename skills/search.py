from __future__ import annotations

from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from db.models import Event


def recent_events(
    db: Session,
    *,
    limit: int = 50,
    camera: Optional[str] = None,
    label: Optional[str] = None,
) -> list[dict[str, Any]]:
    """Return recent events as plain dicts for LLM / API."""
    stmt = select(Event).order_by(Event.id.desc()).limit(limit)
    if camera:
        stmt = stmt.where(Event.camera == camera)
    if label:
        stmt = stmt.where(Event.label == label)
    rows = db.execute(stmt).scalars().all()
    return [_event_to_dict(e) for e in rows]


def _event_to_dict(e: Event) -> dict[str, Any]:
    return {
        "id": e.id,
        "camera": e.camera,
        "label": e.label,
        "start_time": e.start_time.isoformat() if e.start_time else None,
        "end_time": e.end_time.isoformat() if e.end_time else None,
        "confidence": e.confidence,
    }
