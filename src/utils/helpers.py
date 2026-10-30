"""
Common Helper Functions for TRAFFIC TREND Platform
"""
import hashlib
from typing import Any, List, Optional
import pandas as pd
import numpy as np

def compute_checksum(filepath_or_bytes: Any) -> str:
    """Calculates SHA256 checksum for data integrity audits."""
    hasher = hashlib.sha256()
    if isinstance(filepath_or_bytes, (str, bytes)):
        if isinstance(filepath_or_bytes, str):
            with open(filepath_or_bytes, "rb") as f:
                for chunk in iter(lambda: f.read(65536), b""):
                    hasher.update(chunk)
        else:
            hasher.update(filepath_or_bytes)
    elif hasattr(filepath_or_bytes, "read"):
        content = filepath_or_bytes.read()
        if hasattr(filepath_or_bytes, "seek"):
            filepath_or_bytes.seek(0)
        hasher.update(content)
    return hasher.hexdigest()

def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Performs division avoiding division by zero or NaN propagation."""
    try:
        if denominator is None or np.isnan(denominator) or denominator == 0:
            return default
        if numerator is None or np.isnan(numerator):
            return default
        return float(numerator / denominator)
    except Exception:
        return default

def normalize_column_name(col: str) -> str:
    """Standardizes arbitrary column names to snake_case format."""
    clean = str(col).strip().lower()
    clean = clean.replace(" ", "_").replace("-", "_").replace(".", "_").replace("/", "_")
    clean = "".join(c for c in clean if c.isalnum() or c == "_")
    while "__" in clean:
        clean = clean.replace("__", "_")
    return clean.strip("_")

def detect_column_mappings(df_columns: List[str]) -> dict:
    """
    Intelligently maps varying uploaded column nomenclatures to canonical analytics columns.
    Enables zero-friction compatibility across national & regional road crash datasets.
    """
    norm_to_orig = {normalize_column_name(c): c for c in df_columns}
    norm_cols = list(norm_to_orig.keys())
    
    mapping = {}
    
    # Priority synonyms for canonical dimensions
    patterns = {
        "accident_id": ["accident_id", "crash_id", "incident_id", "case_id", "collision_id", "id", "record_id"],
        "accident_date": ["accident_date", "crash_date", "incident_date", "date", "collision_date", "date_time"],
        "accident_time": ["accident_time", "crash_time", "incident_time", "time", "time_of_day"],
        "year": ["year", "accident_year", "crash_year", "yr"],
        "month": ["month", "accident_month", "crash_month", "mon"],
        "day_of_week": ["day_of_week", "day", "weekday", "crash_day"],
        "hour_of_day": ["hour_of_day", "hour", "time_hour", "crash_hour"],
        "state": ["state", "province", "state_name", "region", "jurisdiction", "admin_state"],
        "district": ["district", "county", "district_name", "city", "borough", "police_station", "area"],
        "location_type": ["location_type", "urban_rural", "area_type", "locality", "zone"],
        "latitude": ["latitude", "lat", "y_coord", "gps_latitude", "northing"],
        "longitude": ["longitude", "long", "lon", "x_coord", "gps_longitude", "easting"],
        "road_type": ["road_type", "highway_type", "road_classification", "route_type", "road_category"],
        "road_condition": ["road_condition", "surface_condition", "road_surface", "pavement_condition"],
        "weather": ["weather", "weather_condition", "climate", "atmospheric_conditions"],
        "light_condition": ["light_condition", "lighting", "illumination", "light"],
        "accident_severity": ["accident_severity", "severity", "crash_severity", "injury_severity", "level"],
        "fatalities_count": ["fatalities_count", "fatalities", "persons_killed", "killed", "deaths", "number_of_fatalities", "dead"],
        "injured_count": ["injured_count", "injured", "persons_injured", "injuries", "number_of_injuries", "casualty_count"],
        "vehicles_involved_count": ["vehicles_involved_count", "vehicles_involved", "number_of_vehicles", "vehicles_count", "total_vehicles"],
        "collision_type": ["collision_type", "manner_of_collision", "accident_type", "crash_type", "impact_type"],
        "primary_vehicle_type": ["primary_vehicle_type", "vehicle_type", "vehicle_category", "offending_vehicle", "vehicle"],
        "contributing_factor": ["contributing_factor", "cause", "accident_cause", "primary_cause", "reason", "violation"]
    }
    
    for canon, syns in patterns.items():
        found = False
        for s in syns:
            if s in norm_cols:
                mapping[canon] = norm_to_orig[s]
                found = True
                break
        if not found:
            # Fuzzy match (substring)
            for c_norm in norm_cols:
                if any(syn in c_norm for syn in syns if len(syn) > 3):
                    mapping[canon] = norm_to_orig[c_norm]
                    found = True
                    break
                    
    return mapping

