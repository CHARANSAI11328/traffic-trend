"""
Key Performance Indicators (KPI) Engine for TRAFFIC TREND Platform
Computes dynamic metrics and period-over-period deltas.
"""
from dataclasses import dataclass
from typing import Dict, Any, Optional
import pandas as pd
import numpy as np
from src.utils.helpers import safe_divide

@dataclass
class KPISnapshot:
    """Dynamic executive KPI metrics container."""
    total_accidents: int
    total_fatalities: int
    total_injured: int
    total_casualties: int
    fatal_accidents_count: int
    non_fatal_accidents_count: int
    fatality_rate_pct: float      # Fatalities per 100 accidents
    casualty_rate_per_crash: float
    avg_accidents_per_day: float
    most_affected_region: str
    most_affected_time_window: str
    fatal_accidents_ratio_pct: float
    
    # Period-over-Period Deltas (None if no comparison period available)
    accidents_delta_pct: Optional[float] = None
    fatalities_delta_pct: Optional[float] = None
    injured_delta_pct: Optional[float] = None


class KPICalculator:
    """Calculates all executive summary indicators from filtered DataFrame."""

    @classmethod
    def compute(
        cls,
        df: pd.DataFrame,
        prior_df: Optional[pd.DataFrame] = None
    ) -> KPISnapshot:
        """Computes current KPIs and optional comparison with previous period."""
        if df is None or df.empty:
            return KPISnapshot(
                total_accidents=0,
                total_fatalities=0,
                total_injured=0,
                total_casualties=0,
                fatal_accidents_count=0,
                non_fatal_accidents_count=0,
                fatality_rate_pct=0.0,
                casualty_rate_per_crash=0.0,
                avg_accidents_per_day=0.0,
                most_affected_region="N/A",
                most_affected_time_window="N/A",
                fatal_accidents_ratio_pct=0.0
            )

        total_accidents = len(df)
        
        # Fatalities & Injuries
        fat = pd.to_numeric(df.get("fatalities_count", 0), errors="coerce").fillna(0)
        inj = pd.to_numeric(df.get("injured_count", 0), errors="coerce").fillna(0)
        
        total_fatalities = int(fat.sum())
        total_injured = int(inj.sum())
        total_casualties = total_fatalities + total_injured

        # Fatal Accidents Count
        if "accident_severity" in df.columns:
            fatal_mask = df["accident_severity"].astype(str).str.lower().str.contains("fatal") | (fat > 0)
        else:
            fatal_mask = fat > 0

        fatal_accidents = int(fatal_mask.sum())
        non_fatal_accidents = total_accidents - fatal_accidents

        # Rates
        fatality_rate_pct = round(safe_divide(total_fatalities, total_accidents) * 100.0, 2)
        casualty_rate = round(safe_divide(total_casualties, total_accidents), 2)
        fatal_ratio_pct = round(safe_divide(fatal_accidents, total_accidents) * 100.0, 2)

        # Average accidents per day
        avg_per_day = 0.0
        if "accident_date" in df.columns:
            dates = pd.to_datetime(df["accident_date"], errors="coerce").dropna()
            if not dates.empty:
                span_days = max(1, (dates.max() - dates.min()).days + 1)
                avg_per_day = round(total_accidents / span_days, 1)

        # Most affected region
        most_affected_region = "N/A"
        for geo_col in ["state", "district", "city", "region"]:
            if geo_col in df.columns and not df[geo_col].isna().all():
                top_geo = df[geo_col].value_counts().index
                if len(top_geo) > 0:
                    most_affected_region = str(top_geo[0])
                    break

        # Most affected time window
        most_affected_time = "N/A"
        for t_col in ["time_window", "hour_of_day"]:
            if t_col in df.columns and not df[t_col].isna().all():
                top_t = df[t_col].value_counts().index
                if len(top_t) > 0:
                    most_affected_time = str(top_t[0])
                    break

        # Deltas
        acc_delta = None
        fat_delta = None
        inj_delta = None

        if prior_df is not None and not prior_df.empty:
            prior_acc = len(prior_df)
            prior_fat = int(pd.to_numeric(prior_df.get("fatalities_count", 0), errors="coerce").fillna(0).sum())
            prior_inj = int(pd.to_numeric(prior_df.get("injured_count", 0), errors="coerce").fillna(0).sum())

            if prior_acc > 0:
                acc_delta = round(((total_accidents - prior_acc) / prior_acc) * 100.0, 1)
            if prior_fat > 0:
                fat_delta = round(((total_fatalities - prior_fat) / prior_fat) * 100.0, 1)
            if prior_inj > 0:
                inj_delta = round(((total_injured - prior_inj) / prior_inj) * 100.0, 1)

        return KPISnapshot(
            total_accidents=total_accidents,
            total_fatalities=total_fatalities,
            total_injured=total_injured,
            total_casualties=total_casualties,
            fatal_accidents_count=fatal_accidents,
            non_fatal_accidents_count=non_fatal_accidents,
            fatality_rate_pct=fatality_rate_pct,
            casualty_rate_per_crash=casualty_rate,
            avg_accidents_per_day=avg_per_day,
            most_affected_region=most_affected_region,
            most_affected_time_window=most_affected_time,
            fatal_accidents_ratio_pct=fatal_ratio_pct,
            accidents_delta_pct=acc_delta,
            fatalities_delta_pct=fat_delta,
            injured_delta_pct=inj_delta
        )

