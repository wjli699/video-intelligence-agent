from __future__ import annotations

from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from db.models import Event


def aggregate_by_label(db: Session, *, limit_cameras: int = 20) -> dict[str, Any]:
    """Simple counts by label for dashboards / summaries."""
    stmt = (
        select(Event.label, func.count(Event.id))
        .group_by(Event.label)
        .order_by(func.count(Event.id).desc())
    )
    rows = db.execute(stmt).all()
    by_label = {r[0] or "(none)": r[1] for r in rows}

    cam_stmt = (
        select(Event.camera, func.count(Event.id))
        .group_by(Event.camera)
        .order_by(func.count(Event.id).desc())
        .limit(limit_cameras)
    )
    cam_rows = db.execute(cam_stmt).all()
    by_camera = {r[0] or "(none)": r[1] for r in cam_rows}

    return {
        "by_label": by_label,
        "by_camera": by_camera,
        "distinct_labels": len(by_label),
    }
