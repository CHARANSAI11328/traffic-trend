"""
Data Transformation & Analytical Feature Engineering for TRAFFIC TREND Platform
Enriches raw crash records with standardized categorical and numerical features.
"""
from typing import Optional
import pandas as pd
import numpy as np

class DataTransformer:
    """Enriches and aggregates accident records for high-performance analytics."""

    @classmethod
    def enrich_features(cls, df: pd.DataFrame) -> pd.DataFrame:
        """Adds analytical dimensions and indices."""
        enriched = df.copy()

        # 1. Temporal Bucketing: Time of Day
        if "hour_of_day" in enriched.columns:
            enriched["hour_of_day"] = pd.to_numeric(enriched["hour_of_day"], errors="coerce")
            
            def categorize_time_window(hour):
                if pd.isna(hour):
                    return "Unknown"
                h = int(hour)
                if 7 <= h <= 10:
                    return "Morning Rush (07:00 - 10:00)"
                elif 11 <= h <= 16:
                    return "Midday & Afternoon (11:00 - 16:00)"
                elif 17 <= h <= 21:
                    return "Evening Rush (17:00 - 21:00)"
                else:
                    return "Night & Early Morning (22:00 - 06:00)"

            enriched["time_window"] = enriched["hour_of_day"].apply(categorize_time_window)

        # 2. Weekday vs Weekend
        if "day_of_week" in enriched.columns:
            weekend_days = ["Saturday", "Sunday"]
            enriched["is_weekend"] = enriched["day_of_week"].astype(str).str.strip().isin(weekend_days)
            enriched["day_type"] = enriched["is_weekend"].apply(lambda w: "Weekend" if w else "Weekday")

        # 3. Casualty Severity Index (CSI)
        # Standard weighted transport index: 5 points per fatality, 1 point per injury
        fat = pd.to_numeric(enriched.get("fatalities_count", 0), errors="coerce").fillna(0)
        inj = pd.to_numeric(enriched.get("injured_count", 0), errors="coerce").fillna(0)
        
        enriched["casualty_severity_index"] = (fat * 5.0) + (inj * 1.0)
        enriched["total_casualties"] = fat + inj
        enriched["is_fatal"] = fat > 0

        # 4. Severity Standardization
        if "accident_severity" in enriched.columns:
            def standardize_severity(sev):
                s = str(sev).strip().lower()
                if "fatal" in s:
                    return "Fatal"
                elif "grievous" in s or "serious" in s:
                    return "Grievous Injury"
                elif "minor" in s or "slight" in s:
                    return "Minor Injury"
                else:
                    return "Property Damage Only"

            enriched["standard_severity"] = enriched["accident_severity"].apply(standardize_severity)

        return enriched

    @classmethod
    def aggregate_time_series(cls, df: pd.DataFrame, freq: str = "ME") -> pd.DataFrame:
        """
        Aggregates accident counts, fatalities and injuries by specified time frequency.
        freq: 'D' (daily), 'W' (weekly), 'ME' (monthly), 'YE' (yearly)
        """
        if "accident_date" not in df.columns:
            return pd.DataFrame()

        temp = df.copy()
        temp["accident_date"] = pd.to_datetime(temp["accident_date"], errors="coerce")
        temp = temp.dropna(subset=["accident_date"])

        if temp.empty:
            return pd.DataFrame()

        temp = temp.set_index("accident_date")
        
        # Aggregation metrics
        agg_rules = {
            "accident_id": "count" if "accident_id" in temp.columns else len
        }
        if "fatalities_count" in temp.columns:
            agg_rules["fatalities_count"] = "sum"
        if "injured_count" in temp.columns:
            agg_rules["injured_count"] = "sum"
        if "casualty_severity_index" in temp.columns:
            agg_rules["casualty_severity_index"] = "sum"

        resampled = temp.resample(freq).agg(agg_rules).reset_index()
        rename_map = {"accident_id": "total_accidents"}
        resampled.rename(columns=rename_map, inplace=True)
        return resampled

