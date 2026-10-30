"""
Temporal and Trend Analysis Engine for TRAFFIC TREND Platform
Analyzes longitudinal, seasonal, diurnal, and periodic accident behaviors.
"""
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

class TrendAnalyzer:
    """Calculates temporal distributions and moving averages."""

    @classmethod
    def analyze_yearly_trend(cls, df: pd.DataFrame) -> pd.DataFrame:
        """Aggregates accidents, fatalities, and injuries by Year."""
        if "year" not in df.columns:
            return pd.DataFrame()

        valid = df.dropna(subset=["year"]).copy()
        valid["year"] = pd.to_numeric(valid["year"], errors="coerce").dropna().astype(int)

        grouped = valid.groupby("year").agg(
            total_accidents=("accident_id" if "accident_id" in valid.columns else "year", "count"),
            fatalities=("fatalities_count", lambda x: pd.to_numeric(x, errors="coerce").fillna(0).sum()) if "fatalities_count" in valid.columns else ("year", lambda x: 0),
            injuries=("injured_count", lambda x: pd.to_numeric(x, errors="coerce").fillna(0).sum()) if "injured_count" in valid.columns else ("year", lambda x: 0),
        ).reset_index().sort_values("year")

        # Compute Year-over-Year (YoY) Growth %
        grouped["accidents_yoy_pct"] = grouped["total_accidents"].pct_change() * 100.0
        grouped["fatalities_yoy_pct"] = grouped["fatalities"].pct_change() * 100.0
        grouped["fatality_rate_pct"] = (grouped["fatalities"] / grouped["total_accidents"].replace(0, np.nan)) * 100.0

        return grouped

    @classmethod
    def analyze_monthly_trend(cls, df: pd.DataFrame) -> pd.DataFrame:
        """Aggregates accidents by Month (order: Jan - Dec)."""
        if "month" not in df.columns:
            return pd.DataFrame()

        valid = df.dropna(subset=["month"]).copy()
        
        month_order = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]

        grouped = valid.groupby("month").agg(
            total_accidents=("accident_id" if "accident_id" in valid.columns else "month", "count"),
            fatalities=("fatalities_count", lambda x: pd.to_numeric(x, errors="coerce").fillna(0).sum()) if "fatalities_count" in valid.columns else ("month", lambda x: 0),
            injuries=("injured_count", lambda x: pd.to_numeric(x, errors="coerce").fillna(0).sum()) if "injured_count" in valid.columns else ("month", lambda x: 0),
        ).reset_index()

        # Categorical sort
        grouped["month_num"] = grouped["month"].apply(lambda m: month_order.index(m) + 1 if m in month_order else 99)
        grouped = grouped.sort_values("month_num").drop(columns=["month_num"])
        return grouped

    @classmethod
    def analyze_day_of_week(cls, df: pd.DataFrame) -> pd.DataFrame:
        """Aggregates accidents by Day of Week (Monday - Sunday)."""
        if "day_of_week" not in df.columns:
            return pd.DataFrame()

        valid = df.dropna(subset=["day_of_week"]).copy()
        day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

        grouped = valid.groupby("day_of_week").agg(
            total_accidents=("accident_id" if "accident_id" in valid.columns else "day_of_week", "count"),
            fatalities=("fatalities_count", lambda x: pd.to_numeric(x, errors="coerce").fillna(0).sum()) if "fatalities_count" in valid.columns else ("day_of_week", lambda x: 0),
            injuries=("injured_count", lambda x: pd.to_numeric(x, errors="coerce").fillna(0).sum()) if "injured_count" in valid.columns else ("day_of_week", lambda x: 0),
        ).reset_index()

        grouped["day_num"] = grouped["day_of_week"].apply(lambda d: day_order.index(d) if d in day_order else 99)
        grouped = grouped.sort_values("day_num").drop(columns=["day_num"])
        return grouped

    @classmethod
    def analyze_hourly_distribution(cls, df: pd.DataFrame) -> pd.DataFrame:
        """Aggregates accidents across 24 hours."""
        if "hour_of_day" not in df.columns:
            return pd.DataFrame()

        valid = df.dropna(subset=["hour_of_day"]).copy()
        valid["hour_of_day"] = pd.to_numeric(valid["hour_of_day"], errors="coerce").dropna().astype(int)
        valid = valid[(valid["hour_of_day"] >= 0) & (valid["hour_of_day"] <= 23)]

        grouped = valid.groupby("hour_of_day").agg(
            total_accidents=("accident_id" if "accident_id" in valid.columns else "hour_of_day", "count"),
            fatalities=("fatalities_count", lambda x: pd.to_numeric(x, errors="coerce").fillna(0).sum()) if "fatalities_count" in valid.columns else ("hour_of_day", lambda x: 0),
            injuries=("injured_count", lambda x: pd.to_numeric(x, errors="coerce").fillna(0).sum()) if "injured_count" in valid.columns else ("hour_of_day", lambda x: 0),
        ).reset_index().sort_values("hour_of_day")

        # Fill all 24 hours even if some have 0
        all_hours = pd.DataFrame({"hour_of_day": list(range(24))})
        merged = all_hours.merge(grouped, on="hour_of_day", how="left").fillna(0)
        merged["hour_label"] = merged["hour_of_day"].apply(lambda h: f"{h:02d}:00")
        return merged

    @classmethod
    def compute_moving_averages(cls, df: pd.DataFrame, window: int = 7) -> pd.DataFrame:
        """Computes rolling moving average on daily accident time-series."""
        if "accident_date" not in df.columns:
            return pd.DataFrame()

        daily = df.groupby(pd.to_datetime(df["accident_date"]).dt.date).size().reset_index(name="daily_accidents")
        daily.rename(columns={"accident_date": "date"}, inplace=True)
        daily["date"] = pd.to_datetime(daily["date"])
        daily = daily.sort_values("date")
        
        daily[f"ma_{window}d"] = daily["daily_accidents"].rolling(window=window, min_periods=1).mean()
        return daily

