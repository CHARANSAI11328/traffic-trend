from dataclasses import dataclass
from typing import Dict, Any, Optional
import pandas as pd
import numpy as np
from backend.app.core.helpers import safe_divide

@dataclass
class KPISnapshot:
    """Dynamic executive KPI metrics container."""
    total_accidents: int
    total_fatalities: int
    total_injured: int
    total_casualties: int
    fatal_accidents_count: int
    non_fatal_accidents_count: int
    fatality_rate_pct: float
    casualty_rate_per_crash: float
    avg_accidents_per_day: float
    most_affected_region: str
    most_affected_time_window: str
    fatal_accidents_ratio_pct: float
    data_coverage_period: str
    
    # Period-over-Period Deltas
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
                fatal_accidents_ratio_pct=0.0,
                data_coverage_period="N/A"
            )

        total_accidents = len(df)
        
        fat = pd.to_numeric(df.get("fatalities_count", 0), errors="coerce").fillna(0)
        inj = pd.to_numeric(df.get("injured_count", 0), errors="coerce").fillna(0)
        
        total_fatalities = int(fat.sum())
        total_injured = int(inj.sum())
        total_casualties = total_fatalities + total_injured

        # Fatal Accidents Count
        if "accident_severity" in df.columns:
            fatal_mask = df["accident_severity"].astype(str).str.lower().str.contains("fatal")
            fatal_accidents = int(fatal_mask.sum())
        else:
            fatal_accidents = int((fat > 0).sum())
            
        non_fatal_accidents = total_accidents - fatal_accidents

        # Rates
        fatality_rate_pct = round(safe_divide(total_fatalities, total_accidents) * 100.0, 2)
        casualty_rate = round(safe_divide(total_casualties, total_accidents), 2)
        fatal_accidents_ratio = round(safe_divide(fatal_accidents, total_accidents) * 100.0, 2)

        # Average accidents per day
        if "accident_date" in df.columns:
            dates = pd.to_datetime(df["accident_date"], errors="coerce").dropna()
            if not dates.empty:
                min_date = dates.min()
                max_date = dates.max()
                days_span = max((max_date - min_date).days + 1, 1)
                avg_per_day = round(total_accidents / days_span, 2)
                coverage = f"{min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')}"
            else:
                avg_per_day = round(total_accidents / 365.0, 2)
                coverage = "Date range unspecified"
        else:
            avg_per_day = round(total_accidents / 365.0, 2)
            coverage = "Date range unspecified"

        # Most Affected Region
        if "state" in df.columns and not df["state"].dropna().empty:
            top_state = df["state"].value_counts().idxmax()
            state_cnt = df["state"].value_counts().max()
            most_affected_region = f"{top_state} ({state_cnt} crashes)"
        elif "district" in df.columns and not df["district"].dropna().empty:
            top_dist = df["district"].value_counts().idxmax()
            most_affected_region = f"{top_dist}"
        else:
            most_affected_region = "Regional attribute not available"

        # Most Affected Time Window
        if "hour_of_day" in df.columns and not df["hour_of_day"].dropna().empty:
            hr_series = pd.to_numeric(df["hour_of_day"], errors="coerce").dropna()
            if not hr_series.empty:
                top_hr = int(hr_series.value_counts().idxmax())
                most_affected_time_window = f"{top_hr:02d}:00 - {top_hr+1:02d}:00"
            else:
                most_affected_time_window = "Time attribute not available"
        else:
            most_affected_time_window = "Time attribute not available"

        # Period-over-period deltas
        accidents_delta = None
        fatalities_delta = None
        injured_delta = None

        if prior_df is not None and not prior_df.empty:
            prior_total = len(prior_df)
            prior_fat = int(pd.to_numeric(prior_df.get("fatalities_count", 0), errors="coerce").fillna(0).sum())
            prior_inj = int(pd.to_numeric(prior_df.get("injured_count", 0), errors="coerce").fillna(0).sum())

            if prior_total > 0:
                accidents_delta = round(((total_accidents - prior_total) / prior_total) * 100.0, 1)
            if prior_fat > 0:
                fatalities_delta = round(((total_fatalities - prior_fat) / prior_fat) * 100.0, 1)
            if prior_inj > 0:
                injured_delta = round(((total_injured - prior_inj) / prior_inj) * 100.0, 1)

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
            most_affected_time_window=most_affected_time_window,
            fatal_accidents_ratio_pct=fatal_accidents_ratio,
            data_coverage_period=coverage,
            accidents_delta_pct=accidents_delta,
            fatalities_delta_pct=fatalities_delta,
            injured_delta_pct=injured_delta
        )
