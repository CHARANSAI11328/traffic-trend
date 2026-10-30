"""
System Health and Diagnostic Engine for TRAFFIC TREND Platform
Monitors memory, database latency, disk IO and application runtime metrics.
"""
from datetime import datetime, timezone
from typing import Dict, Any
import os
import time
from src.database.connection import check_database_health
from src.database.repository import DatasetRepository
from src.utils.configuration import CONFIG, LOGS_DIR, DATA_DIR

class SystemHealthMonitor:
    """Provides operational telemetry and diagnostics."""

    @classmethod
    def get_full_health_status(cls) -> Dict[str, Any]:
        """Collects complete operational health matrix."""
        # 1. Database Health
        db_health = check_database_health()

        # 2. Filesystem Health
        fs_healthy = True
        fs_error = None
        try:
            test_file = LOGS_DIR / f".health_check_{int(time.time())}"
            test_file.write_text("ok", encoding="utf-8")
            test_file.unlink(missing_ok=True)
        except Exception as e:
            fs_healthy = False
            fs_error = str(e)

        # 3. Active Dataset Status
        active_dataset = DatasetRepository.get_active_dataset()
        dataset_status = {
            "is_loaded": active_dataset is not None,
            "name": active_dataset["dataset_name"] if active_dataset else "No Active Dataset",
            "records": active_dataset["record_count"] if active_dataset else 0,
            "source_type": active_dataset["source_type"] if active_dataset else "None",
            "last_updated": active_dataset["updated_at"].strftime("%Y-%m-%d %H:%M UTC") if active_dataset and active_dataset["updated_at"] else "Never"
        }

        # 4. Overall Health Grade
        all_ok = db_health["connected"] and fs_healthy
        system_status = "OPERATIONAL" if all_ok else "DEGRADED"

        return {
            "system_status": system_status,
            "app_version": CONFIG.VERSION,
            "environment": CONFIG.ENVIRONMENT,
            "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
            "database": db_health,
            "filesystem": {
                "status": "HEALTHY" if fs_healthy else "ERROR",
                "writable": fs_healthy,
                "error": fs_error
            },
            "active_dataset": dataset_status
        }
