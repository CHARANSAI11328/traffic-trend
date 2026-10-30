"""
Data Freshness & Source Ingestion Audit for TRAFFIC TREND Platform
Tracks dataset age, refresh latency, and external connector status.
"""
from datetime import datetime, timezone
from typing import Dict, Any, Optional
import pandas as pd
from src.database.repository import DatasetRepository

class DataFreshnessAuditor:
    """Evaluates temporal currency and update cadences."""

    @classmethod
    def evaluate_freshness(cls, df: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        """Calculates dataset age and connection state."""
        active = DatasetRepository.get_active_dataset()
        now_utc = datetime.now(timezone.utc).replace(tzinfo=None)

        if not active:
            return {
                "feed_mode": "Historical / Uploaded Dataset — Live Feed Not Connected",
                "is_live_connected": False,
                "dataset_name": "None",
                "last_import_time": "Never",
                "freshness_tier": "No Data",
                "days_since_import": None,
                "latest_incident_date": "N/A"
            }

        last_import = active.get("updated_at") or active.get("created_at")
        days_since_import = (now_utc - last_import).days if last_import else 0

        # Assess date of latest incident in dataset
        latest_incident_str = "N/A"
        if df is not None and not df.empty and "accident_date" in df.columns:
            dates = pd.to_datetime(df["accident_date"], errors="coerce").dropna()
            if not dates.empty:
                latest_incident_str = dates.max().strftime("%Y-%m-%d")

        # Categorize freshness tier
        if days_since_import < 1:
            tier = "Fresh (< 24 Hours)"
        elif days_since_import < 7:
            tier = "Recent (< 7 Days)"
        elif days_since_import < 30:
            tier = "Current (< 30 Days)"
        else:
            tier = "Archival / Historical"

        return {
            "feed_mode": "Historical / Uploaded Dataset — Live Feed Not Connected",
            "is_live_connected": False,
            "dataset_name": active.get("dataset_name"),
            "source_type": active.get("source_type"),
            "last_import_time": last_import.strftime("%Y-%m-%d %H:%M UTC") if last_import else "Unknown",
            "days_since_import": days_since_import,
            "freshness_tier": tier,
            "latest_incident_date": latest_incident_str
        }
