from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np
from backend.app.core.helpers import safe_divide

class GeographicalAnalyzer:
    """Computes spatial rankings, administrative summaries, and hotspot clusters."""

    @classmethod
    def analyze_by_state(cls, df: pd.DataFrame) -> List[Dict[str, Any]]:
        if "state" not in df.columns or df.empty:
            return []

        valid = df.dropna(subset=["state"]).copy()
        grouped = valid.groupby("state").agg(
            total_accidents=("accident_id" if "accident_id" in valid.columns else "state", "count"),
            fatalities=("fatalities_count", lambda x: pd.to_numeric(x, errors="coerce").fillna(0).sum()) if "fatalities_count" in valid.columns else ("state", lambda x: 0),
            injuries=("injured_count", lambda x: pd.to_numeric(x, errors="coerce").fillna(0).sum()) if "injured_count" in valid.columns else ("state", lambda x: 0),
        ).reset_index()

        grouped["total_casualties"] = grouped["fatalities"] + grouped["injuries"]
        grouped["fatality_rate_pct"] = (grouped["fatalities"] / grouped["total_accidents"].replace(0, np.nan)) * 100.0
        grouped["fatality_rate_pct"] = grouped["fatality_rate_pct"].fillna(0.0).round(2)
        
        # Risk Score: Weighted formula (accidents * 0.4 + fatalities * 2.5 + injuries * 0.8)
        grouped["risk_score"] = (
            (grouped["total_accidents"] * 0.4) +
            (grouped["fatalities"] * 2.5) +
            (grouped["injuries"] * 0.8)
        ).round(1)

        grouped = grouped.sort_values("total_accidents", ascending=False)
        return grouped.to_dict(orient="records")

    @classmethod
    def analyze_by_district(cls, df: pd.DataFrame, state_filter: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        if "district" not in df.columns or df.empty:
            return []

        valid = df.dropna(subset=["district"]).copy()
        if state_filter and state_filter != "All" and "state" in valid.columns:
            valid = valid[valid["state"] == state_filter]

        grouped = valid.groupby(["district", "state"] if "state" in valid.columns else ["district"]).agg(
            total_accidents=("accident_id" if "accident_id" in valid.columns else "district", "count"),
            fatalities=("fatalities_count", lambda x: pd.to_numeric(x, errors="coerce").fillna(0).sum()) if "fatalities_count" in valid.columns else ("district", lambda x: 0),
            injuries=("injured_count", lambda x: pd.to_numeric(x, errors="coerce").fillna(0).sum()) if "injured_count" in valid.columns else ("district", lambda x: 0),
        ).reset_index()

        grouped["fatality_rate_pct"] = (grouped["fatalities"] / grouped["total_accidents"].replace(0, np.nan)) * 100.0
        grouped["fatality_rate_pct"] = grouped["fatality_rate_pct"].fillna(0.0).round(2)
        grouped = grouped.sort_values("total_accidents", ascending=False).head(limit)
        return grouped.to_dict(orient="records")

    @classmethod
    def get_map_points(cls, df: pd.DataFrame, limit: int = 1500) -> List[Dict[str, Any]]:
        """Extracts valid geo-coordinates for MapLibre GL rendering."""
        if "latitude" not in df.columns or "longitude" not in df.columns or df.empty:
            return []

        valid = df.dropna(subset=["latitude", "longitude"]).copy()
        valid["latitude"] = pd.to_numeric(valid["latitude"], errors="coerce")
        valid["longitude"] = pd.to_numeric(valid["longitude"], errors="coerce")
        
        # Valid bounds
        valid = valid[
            (valid["latitude"] >= -90) & (valid["latitude"] <= 90) &
            (valid["longitude"] >= -180) & (valid["longitude"] <= 180)
        ]

        if len(valid) > limit:
            valid = valid.sample(n=limit, random_state=42)

        points = []
        for _, row in valid.iterrows():
            points.append({
                "id": str(row.get("accident_id", "")),
                "latitude": float(row["latitude"]),
                "longitude": float(row["longitude"]),
                "severity": str(row.get("accident_severity", "Unknown")),
                "fatalities": int(row.get("fatalities_count", 0)),
                "injured": int(row.get("injured_count", 0)),
                "state": str(row.get("state", "")),
                "district": str(row.get("district", "")),
                "road_type": str(row.get("road_type", "")),
                "collision_type": str(row.get("collision_type", ""))
            })
        return points

    @classmethod
    def detect_hotspots(cls, df: pd.DataFrame, top_n: int = 10) -> List[Dict[str, Any]]:
        """Identifies top spatial crash clusters."""
        if df.empty:
            return []

        # If district and road_type exist, cluster by high-density intersection
        if "district" in df.columns and "road_type" in df.columns:
            grouped = df.groupby(["district", "road_type", "state"]).agg(
                accident_count=("accident_id" if "accident_id" in df.columns else "district", "count"),
                fatalities=("fatalities_count", lambda x: pd.to_numeric(x, errors="coerce").fillna(0).sum()) if "fatalities_count" in df.columns else ("district", lambda x: 0),
                lat_mean=("latitude", "mean") if "latitude" in df.columns else ("district", lambda x: None),
                lon_mean=("longitude", "mean") if "longitude" in df.columns else ("district", lambda x: None)
            ).reset_index()

            grouped["severity_index"] = (grouped["accident_count"] * 1.0) + (grouped["fatalities"] * 3.0)
            top = grouped.sort_values("severity_index", ascending=False).head(top_n)
            
            hotspots = []
            for _, r in top.iterrows():
                hotspots.append({
                    "corridor": f"{r['district']} — {r['road_type']}",
                    "state": r["state"],
                    "accidents": int(r["accident_count"]),
                    "fatalities": int(r["fatalities"]),
                    "latitude": float(r["lat_mean"]) if pd.notna(r["lat_mean"]) else None,
                    "longitude": float(r["lon_mean"]) if pd.notna(r["lon_mean"]) else None,
                    "risk_level": "Critical" if r["fatalities"] >= 10 else "High"
                })
            return hotspots
        return []
