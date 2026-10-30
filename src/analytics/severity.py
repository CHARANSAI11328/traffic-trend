"""
Accident Severity & Casualty Analysis Engine for TRAFFIC TREND Platform
Analyzes morbidity, mortality, vulnerable road users, and severity predictors.
"""
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

class SeverityAnalyzer:
    """Analyzes distribution of fatal, grievous, minor and property damage incidents."""

    @classmethod
    def analyze_severity_distribution(cls, df: pd.DataFrame) -> pd.DataFrame:
        """Aggregates crashes by severity class."""
        sev_col = next((c for c in ["accident_severity", "severity", "standard_severity"] if c in df.columns), None)
        if not sev_col:
            return pd.DataFrame()

        valid = df.dropna(subset=[sev_col]).copy()
        valid[sev_col] = valid[sev_col].astype(str).str.strip().str.title()

        grouped = valid.groupby(sev_col).agg(
            total_accidents=("accident_id" if "accident_id" in valid.columns else sev_col, "count"),
            fatalities=("fatalities_count", lambda x: pd.to_numeric(x, errors="coerce").fillna(0).sum()) if "fatalities_count" in valid.columns else (sev_col, lambda x: 0),
            injuries=("injured_count", lambda x: pd.to_numeric(x, errors="coerce").fillna(0).sum()) if "injured_count" in valid.columns else (sev_col, lambda x: 0),
        ).reset_index()

        total_acc = grouped["total_accidents"].sum()
        grouped["pct_of_total"] = round((grouped["total_accidents"] / total_acc) * 100.0, 1)
        grouped["fatality_rate_pct"] = round((grouped["fatalities"] / grouped["total_accidents"].replace(0, np.nan)) * 100.0, 1)

        return grouped

    @classmethod
    def analyze_by_vehicle_type(cls, df: pd.DataFrame) -> pd.DataFrame:
        """Evaluates casualty impact by primary vehicle category involved."""
        veh_col = next((c for c in ["primary_vehicle_type", "vehicle_type", "vehicle_category"] if c in df.columns), None)
        if not veh_col:
            return pd.DataFrame()

        valid = df.dropna(subset=[veh_col]).copy()
        valid[veh_col] = valid[veh_col].astype(str).str.strip()

        grouped = valid.groupby(veh_col).agg(
            total_accidents=("accident_id" if "accident_id" in valid.columns else veh_col, "count"),
            fatalities=("fatalities_count", lambda x: pd.to_numeric(x, errors="coerce").fillna(0).sum()) if "fatalities_count" in valid.columns else (veh_col, lambda x: 0),
            injuries=("injured_count", lambda x: pd.to_numeric(x, errors="coerce").fillna(0).sum()) if "injured_count" in valid.columns else (veh_col, lambda x: 0),
        ).reset_index()

        grouped["total_casualties"] = grouped["fatalities"] + grouped["injuries"]
        grouped["fatality_rate_pct"] = round((grouped["fatalities"] / grouped["total_accidents"].replace(0, np.nan)) * 100.0, 1)
        grouped = grouped.sort_values("total_accidents", ascending=False).reset_index(drop=True)
        return grouped

    @classmethod
    def analyze_by_road_and_weather(cls, df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """Calculates crash frequency and fatality risk across road types and weather conditions."""
        res = {}
        
        # Road Type
        road_col = next((c for c in ["road_type", "highway_type", "road_category"] if c in df.columns), None)
        if road_col:
            valid_r = df.dropna(subset=[road_col]).copy()
            grp_r = valid_r.groupby(road_col).agg(
                total_accidents=("accident_id" if "accident_id" in valid_r.columns else road_col, "count"),
                fatalities=("fatalities_count", lambda x: pd.to_numeric(x, errors="coerce").fillna(0).sum()) if "fatalities_count" in valid_r.columns else (road_col, lambda x: 0),
                injuries=("injured_count", lambda x: pd.to_numeric(x, errors="coerce").fillna(0).sum()) if "injured_count" in valid_r.columns else (road_col, lambda x: 0),
            ).reset_index()
            grp_r["fatality_rate_pct"] = round((grp_r["fatalities"] / grp_r["total_accidents"].replace(0, np.nan)) * 100.0, 1)
            res["road_type"] = grp_r.sort_values("total_accidents", ascending=False)

        # Weather
        weath_col = next((c for c in ["weather", "weather_condition", "climate"] if c in df.columns), None)
        if weath_col:
            valid_w = df.dropna(subset=[weath_col]).copy()
            grp_w = valid_w.groupby(weath_col).agg(
                total_accidents=("accident_id" if "accident_id" in valid_w.columns else weath_col, "count"),
                fatalities=("fatalities_count", lambda x: pd.to_numeric(x, errors="coerce").fillna(0).sum()) if "fatalities_count" in valid_w.columns else (weath_col, lambda x: 0),
                injuries=("injured_count", lambda x: pd.to_numeric(x, errors="coerce").fillna(0).sum()) if "injured_count" in valid_w.columns else (weath_col, lambda x: 0),
            ).reset_index()
            grp_w["fatality_rate_pct"] = round((grp_w["fatalities"] / grp_w["total_accidents"].replace(0, np.nan)) * 100.0, 1)
            res["weather"] = grp_w.sort_values("total_accidents", ascending=False)

        return res

