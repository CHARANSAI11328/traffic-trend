import time
import os
import shutil
from typing import Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text
from backend.app.core.config import settings

class SystemHealthMonitor:
    """Monitors system performance, database latency, and storage resources."""

    @classmethod
    def check_health(cls, db: Session) -> Dict[str, Any]:
        start = time.perf_counter()
        db_status = "healthy"
        db_latency_ms = 0.0
        db_type = "PostgreSQL" if "postgresql" in settings.DATABASE_URL else "SQLite"

        try:
            db.execute(text("SELECT 1"))
            db_latency_ms = round((time.perf_counter() - start) * 1000, 2)
        except Exception as e:
            db_status = f"unhealthy: {str(e)}"

        # Disk usage for exports/data
        try:
            usage = shutil.disk_usage(str(settings.DATA_DIR))
            free_gb = round(usage.free / (1024**3), 2)
            total_gb = round(usage.total / (1024**3), 2)
        except Exception:
            free_gb = 0.0
            total_gb = 0.0

        return {
            "status": "healthy" if db_status == "healthy" else "degraded",
            "environment": settings.ENVIRONMENT,
            "version": "2.0.0-fullstack",
            "database": {
                "type": db_type,
                "status": db_status,
                "latency_ms": db_latency_ms
            },
            "storage": {
                "free_disk_gb": free_gb,
                "total_disk_gb": total_gb
            },
            "timestamp": time.time()
        }
