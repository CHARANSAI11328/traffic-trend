from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from backend.app.core.helpers import safe_divide

class SeverityAnalyzer:
    """Analyzes casualty distributions, fatality ratios, and severity drivers."""

    @classmethod
    def analyze_severity_distribution(cls, df: pd.DataFrame) -> List[Dict[str, Any]]:
        if "accident_severity" not in df.columns or df.empty:
            return []

        grouped = df.groupby("accident_severity").agg(
            accident_count=("accident_id" if "accident_id" in df.columns else "accident_severity", "count"),
            fatalities=("fatalities_count", lambda x: pd.to_numeric(x, errors="coerce").fillna(0).sum()) if "fatalities_count" in df.columns else ("accident_severity", lambda x: 0),
            injuries=("injured_count", lambda x: pd.to_numeric(x, errors="coerce").fillna(0).sum()) if "injured_count" in df.columns else ("accident_severity", lambda x: 0),
        ).reset_index()

        total = len(df)
        grouped["pct_of_total_crashes"] = (grouped["accident_count"] / total * 100.0).round(2)
        grouped = grouped.sort_values("accident_count", ascending=False)
        return grouped.to_dict(orient="records")

    @classmethod
    def analyze_by_vehicle_type(cls, df: pd.DataFrame) -> List[Dict[str, Any]]:
        if "primary_vehicle_type" not in df.columns or df.empty:
            return []

        grouped = df.groupby("primary_vehicle_type").agg(
            total_accidents=("accident_id" if "accident_id" in df.columns else "primary_vehicle_type", "count"),
            fatalities=("fatalities_count", lambda x: pd.to_numeric(x, errors="coerce").fillna(0).sum()) if "fatalities_count" in df.columns else ("primary_vehicle_type", lambda x: 0),
            injuries=("injured_count", lambda x: pd.to_numeric(x, errors="coerce").fillna(0).sum()) if "injured_count" in df.columns else ("primary_vehicle_type", lambda x: 0),
        ).reset_index()

        grouped["fatality_rate_pct"] = (grouped["fatalities"] / grouped["total_accidents"].replace(0, np.nan) * 100.0).fillna(0).round(2)
        grouped = grouped.sort_values("total_accidents", ascending=False)
        return grouped.to_dict(orient="records")

    @classmethod
    def analyze_by_road_type(cls, df: pd.DataFrame) -> List[Dict[str, Any]]:
        if "road_type" not in df.columns or df.empty:
            return []

        grouped = df.groupby("road_type").agg(
            total_accidents=("accident_id" if "accident_id" in df.columns else "road_type", "count"),
            fatalities=("fatalities_count", lambda x: pd.to_numeric(x, errors="coerce").fillna(0).sum()) if "fatalities_count" in df.columns else ("road_type", lambda x: 0),
            injuries=("injured_count", lambda x: pd.to_numeric(x, errors="coerce").fillna(0).sum()) if "injured_count" in df.columns else ("road_type", lambda x: 0),
        ).reset_index()

        grouped["fatality_rate_pct"] = (grouped["fatalities"] / grouped["total_accidents"].replace(0, np.nan) * 100.0).fillna(0).round(2)
        grouped = grouped.sort_values("total_accidents", ascending=False)
        return grouped.to_dict(orient="records")

    @classmethod
    def analyze_by_weather(cls, df: pd.DataFrame) -> List[Dict[str, Any]]:
        if "weather" not in df.columns or df.empty:
            return []

        grouped = df.groupby("weather").agg(
            total_accidents=("accident_id" if "accident_id" in df.columns else "weather", "count"),
            fatalities=("fatalities_count", lambda x: pd.to_numeric(x, errors="coerce").fillna(0).sum()) if "fatalities_count" in df.columns else ("weather", lambda x: 0),
            injuries=("injured_count", lambda x: pd.to_numeric(x, errors="coerce").fillna(0).sum()) if "injured_count" in df.columns else ("weather", lambda x: 0),
        ).reset_index()

        grouped["fatality_rate_pct"] = (grouped["fatalities"] / grouped["total_accidents"].replace(0, np.nan) * 100.0).fillna(0).round(2)
        grouped = grouped.sort_values("total_accidents", ascending=False)
        return grouped.to_dict(orient="records")
