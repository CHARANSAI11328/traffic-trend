"""
Geographical Analytics & Spatial Concentration Engine for TRAFFIC TREND Platform
Handles regional distributions, administrative hierarchies, and coordinate mapping.
"""
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

class GeographicalAnalyzer:
    """Calculates spatial metrics, regional concentrations, and hotspot data."""

    @classmethod
    def analyze_by_region(cls, df: pd.DataFrame, region_col: str = "state") -> pd.DataFrame:
        """Aggregates accidents, fatalities, injuries, and severity metrics by administrative region."""
        if region_col not in df.columns:
            return pd.DataFrame()

        valid = df.dropna(subset=[region_col]).copy()
        valid[region_col] = valid[region_col].astype(str).str.strip()

        grouped = valid.groupby(region_col).agg(
            total_accidents=("accident_id" if "accident_id" in valid.columns else region_col, "count"),
            fatalities=("fatalities_count", lambda x: pd.to_numeric(x, errors="coerce").fillna(0).sum()) if "fatalities_count" in valid.columns else (region_col, lambda x: 0),
            injuries=("injured_count", lambda x: pd.to_numeric(x, errors="coerce").fillna(0).sum()) if "injured_count" in valid.columns else (region_col, lambda x: 0),
        ).reset_index()

        total_all_acc = grouped["total_accidents"].sum()
        grouped["pct_of_total_accidents"] = round((grouped["total_accidents"] / total_all_acc) * 100.0, 2)
        grouped["fatality_rate_pct"] = round((grouped["fatalities"] / grouped["total_accidents"].replace(0, np.nan)) * 100.0, 2)
        
        # Sort by total accidents descending
        grouped = grouped.sort_values("total_accidents", ascending=False).reset_index(drop=True)
        grouped["rank"] = grouped.index + 1
        return grouped

    @classmethod
    def analyze_urban_vs_rural(cls, df: pd.DataFrame) -> pd.DataFrame:
        """Compares crash characteristics between Urban and Rural areas."""
        loc_col = next((c for c in ["location_type", "urban_rural", "area_type"] if c in df.columns), None)
        if not loc_col:
            return pd.DataFrame()

        valid = df.dropna(subset=[loc_col]).copy()
        grouped = valid.groupby(loc_col).agg(
            total_accidents=("accident_id" if "accident_id" in valid.columns else loc_col, "count"),
            fatalities=("fatalities_count", lambda x: pd.to_numeric(x, errors="coerce").fillna(0).sum()) if "fatalities_count" in valid.columns else (loc_col, lambda x: 0),
            injuries=("injured_count", lambda x: pd.to_numeric(x, errors="coerce").fillna(0).sum()) if "injured_count" in valid.columns else (loc_col, lambda x: 0),
        ).reset_index()

        grouped["fatality_rate_pct"] = round((grouped["fatalities"] / grouped["total_accidents"].replace(0, np.nan)) * 100.0, 2)
        return grouped

    @classmethod
    def extract_hotspots_coordinates(
        cls,
        df: pd.DataFrame,
        min_cluster_size: int = 1
    ) -> pd.DataFrame:
        """
        Filters and prepares coordinate-based geospatial points.
        Excludes null or out-of-bounds coordinates.
        """
        if "latitude" not in df.columns or "longitude" not in df.columns:
            return pd.DataFrame()

        coords = df.dropna(subset=["latitude", "longitude"]).copy()
        coords["latitude"] = pd.to_numeric(coords["latitude"], errors="coerce")
        coords["longitude"] = pd.to_numeric(coords["longitude"], errors="coerce")

        valid_mask = (
            (~coords["latitude"].isna()) &
            (~coords["longitude"].isna()) &
            (coords["latitude"] >= -90.0) &
            (coords["latitude"] <= 90.0) &
            (coords["longitude"] >= -180.0) &
            (coords["longitude"] <= 180.0)
        )
        valid_coords = coords[valid_mask].copy()

        return valid_coords

