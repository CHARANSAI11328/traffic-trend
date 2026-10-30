import asyncio
import json
from typing import AsyncGenerator
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from backend.app.database.connection import get_db
from backend.app.database.repository import DatabaseRepository
from backend.app.monitoring.health import SystemHealthMonitor
from backend.app.monitoring.data_freshness import DataFreshnessAuditor

router = APIRouter()

@router.get("/status")
def get_system_status(db: Session = Depends(get_db)):
    return SystemHealthMonitor.check_health(db)

@router.get("/data-freshness")
def get_data_freshness(db: Session = Depends(get_db)):
    repo = DatabaseRepository(db)
    active = repo.get_active_dataset()
    df = repo.get_records_df(dataset_id=active.id if active else None, limit=1000)
    return DataFreshnessAuditor.audit(active, df)

@router.get("/logs")
def get_system_logs(limit: int = 50, db: Session = Depends(get_db)):
    repo = DatabaseRepository(db)
    logs = repo.get_recent_logs(limit=limit)
    return [
        {
            "id": l.id,
            "level": l.level,
            "message": l.message,
            "module": l.module,
            "created_at": l.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }
        for l in logs
    ]

@router.get("/events")
async def stream_system_events(db: Session = Depends(get_db)):
    """Server-Sent Events (SSE) stream for live updates."""
    async def event_generator() -> AsyncGenerator[str, None]:
        for _ in range(5):
            repo = DatabaseRepository(db)
            health = SystemHealthMonitor.check_health(db)
            data = json.dumps({
                "type": "heartbeat",
                "health": health["status"],
                "db_latency_ms": health["database"]["latency_ms"],
                "timestamp": health["timestamp"]
            })
            yield f"data: {data}\n\n"
            await asyncio.sleep(2)

    return StreamingResponse(event_generator(), media_type="text/event-stream")
