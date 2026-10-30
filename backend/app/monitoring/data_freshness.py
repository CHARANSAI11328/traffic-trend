from typing import Dict, Any, Optional
import pandas as pd
from datetime import datetime, timezone
from backend.app.database.models import DatasetMetadata

class DataFreshnessAuditor:
    """Audits data recency, temporal bounds, and feed connection status."""

    @classmethod
    def audit(cls, active_dataset: Optional[DatasetMetadata], df: pd.DataFrame) -> Dict[str, Any]:
        if active_dataset is None or df.empty:
            return {
                "active_dataset_name": "None",
                "feed_mode": "Historical / Uploaded Data — Live Feed Not Connected",
                "live_feed_connected": False,
                "latest_incident_date": "N/A",
                "earliest_incident_date": "N/A",
                "total_records": 0,
                "last_ingestion_timestamp": "N/A",
                "freshness_status": "No active dataset loaded",
                "disclaimer": "Government road safety statistics are published periodically. Continuous telemetry feeds require authorized institutional API keys."
            }

        dates = pd.to_datetime(df.get("accident_date"), errors="coerce").dropna()
        if not dates.empty:
            latest = dates.max().strftime("%Y-%m-%d")
            earliest = dates.min().strftime("%Y-%m-%d")
        else:
            latest = "Unknown"
            earliest = "Unknown"

        ingested_at = active_dataset.upload_date.strftime("%Y-%m-%d %H:%M:%S UTC") if active_dataset.upload_date else "Unknown"

        return {
            "active_dataset_id": active_dataset.id,
            "active_dataset_name": active_dataset.name,
            "feed_mode": "Historical / Uploaded Data — Live Feed Not Connected",
            "live_feed_connected": False,
            "data_origin": active_dataset.origin or "Manual Upload / Benchmark",
            "earliest_incident_date": earliest,
            "latest_incident_date": latest,
            "total_records": len(df),
            "last_ingestion_timestamp": ingested_at,
            "freshness_status": "Historical Baseline Ingested",
            "disclaimer": "Government road safety statistics are published periodically. Continuous telemetry feeds require authorized institutional API keys."
        }
