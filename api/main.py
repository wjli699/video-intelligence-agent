from __future__ import annotations

import os
from contextlib import asynccontextmanager

from typing import Any

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from db.session import get_session, init_db
from plugins.manager import get_plugin
from skills.aggregate import aggregate_by_label
from skills.search import recent_events


@asynccontextmanager
async def lifespan(_app: FastAPI):
    if os.getenv("INIT_DB_ON_STARTUP", "0") == "1":
        init_db()
    yield


app = FastAPI(
    title="Video Intelligent Agent API",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/summary")
async def get_summary(db: Session = Depends(get_session)) -> dict[str, Any]:
    """Fetch recent events from Postgres and run the configured agent plugin."""
    events = recent_events(db, limit=100)
    if not events:
        return {"summary": None, "events": [], "message": "No events in database yet."}
    plugin = get_plugin()
    try:
        llm = await plugin.summarize(events)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"LLM request failed: {exc}") from exc
    return {"events": events, "llm": llm}


@app.get("/stats")
def get_stats(db: Session = Depends(get_session)) -> dict[str, Any]:
    return aggregate_by_label(db)
