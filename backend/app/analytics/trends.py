from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

class TrendAnalyzer:
    """Calculates temporal distributions, seasonal patterns, and moving averages."""

    @classmethod
    def analyze_yearly_trend(cls, df: pd.DataFrame) -> List[Dict[str, Any]]:
        if "year" not in df.columns or df.empty:
            return []

        valid = df.dropna(subset=["year"]).copy()
        valid["year"] = pd.to_numeric(valid["year"], errors="coerce").dropna().astype(int)

        grouped = valid.groupby("year").agg(
            total_accidents=("accident_id" if "accident_id" in valid.columns else "year", "count"),
            fatalities=("fatalities_count", lambda x: pd.to_numeric(x, errors="coerce").fillna(0).sum()) if "fatalities_count" in valid.columns else ("year", lambda x: 0),
            injuries=("injured_count", lambda x: pd.to_numeric(x, errors="coerce").fillna(0).sum()) if "injured_count" in valid.columns else ("year", lambda x: 0),
        ).reset_index().sort_values("year")

        grouped["accidents_yoy_pct"] = grouped["total_accidents"].pct_change() * 100.0
        grouped["fatalities_yoy_pct"] = grouped["fatalities"].pct_change() * 100.0
        grouped["fatality_rate_pct"] = (grouped["fatalities"] / grouped["total_accidents"].replace(0, np.nan)) * 100.0

        return grouped.replace({np.nan: None}).to_dict(orient="records")

    @classmethod
    def analyze_monthly_trend(cls, df: pd.DataFrame) -> List[Dict[str, Any]]:
        if "month" not in df.columns or df.empty:
            return []

        month_order = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]

        grouped = df.groupby("month").agg(
            total_accidents=("accident_id" if "accident_id" in df.columns else "month", "count"),
            fatalities=("fatalities_count", lambda x: pd.to_numeric(x, errors="coerce").fillna(0).sum()) if "fatalities_count" in df.columns else ("month", lambda x: 0),
            injuries=("injured_count", lambda x: pd.to_numeric(x, errors="coerce").fillna(0).sum()) if "injured_count" in df.columns else ("month", lambda x: 0),
        ).reset_index()

        grouped["month_num"] = grouped["month"].apply(lambda m: month_order.index(m) + 1 if m in month_order else 99)
        grouped = grouped.sort_values("month_num").drop(columns=["month_num"])
        return grouped.to_dict(orient="records")

    @classmethod
    def analyze_day_of_week(cls, df: pd.DataFrame) -> List[Dict[str, Any]]:
        if "day_of_week" not in df.columns or df.empty:
            return []

        days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        grouped = df.groupby("day_of_week").agg(
            total_accidents=("accident_id" if "accident_id" in df.columns else "day_of_week", "count"),
            fatalities=("fatalities_count", lambda x: pd.to_numeric(x, errors="coerce").fillna(0).sum()) if "fatalities_count" in df.columns else ("day_of_week", lambda x: 0),
            injuries=("injured_count", lambda x: pd.to_numeric(x, errors="coerce").fillna(0).sum()) if "injured_count" in df.columns else ("day_of_week", lambda x: 0),
        ).reset_index()

        grouped["day_num"] = grouped["day_of_week"].apply(lambda d: days_order.index(d) + 1 if d in days_order else 99)
        grouped = grouped.sort_values("day_num").drop(columns=["day_num"])
        return grouped.to_dict(orient="records")

    @classmethod
    def analyze_hourly_distribution(cls, df: pd.DataFrame) -> List[Dict[str, Any]]:
        if "hour_of_day" not in df.columns or df.empty:
            return []

        valid = df.dropna(subset=["hour_of_day"]).copy()
        valid["hour_of_day"] = pd.to_numeric(valid["hour_of_day"], errors="coerce").dropna().astype(int)

        grouped = valid.groupby("hour_of_day").agg(
            total_accidents=("accident_id" if "accident_id" in valid.columns else "hour_of_day", "count"),
            fatalities=("fatalities_count", lambda x: pd.to_numeric(x, errors="coerce").fillna(0).sum()) if "fatalities_count" in valid.columns else ("hour_of_day", lambda x: 0),
            injuries=("injured_count", lambda x: pd.to_numeric(x, errors="coerce").fillna(0).sum()) if "injured_count" in valid.columns else ("hour_of_day", lambda x: 0),
        ).reset_index().sort_values("hour_of_day")

        # Flag peak rush hours
        peak_thresh = grouped["total_accidents"].quantile(0.75) if not grouped.empty else 0
        grouped["is_peak_hour"] = grouped["total_accidents"] >= peak_thresh

        return grouped.to_dict(orient="records")

    @classmethod
    def analyze_day_hour_heatmap(cls, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Returns 2D matrix coordinates [day_index, hour, count] for ECharts Heatmap."""
        if "day_of_week" not in df.columns or "hour_of_day" not in df.columns or df.empty:
            return []

        days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        matrix = []

        valid = df.dropna(subset=["day_of_week", "hour_of_day"]).copy()
        valid["hour_of_day"] = pd.to_numeric(valid["hour_of_day"], errors="coerce").dropna().astype(int)

        pivot = valid.groupby(["day_of_week", "hour_of_day"]).size().reset_index(name="count")
        
        for d_idx, day_name in enumerate(days_order):
            for hr in range(24):
                val = pivot[(pivot["day_of_week"] == day_name) & (pivot["hour_of_day"] == hr)]["count"]
                cnt = int(val.values[0]) if not val.empty else 0
                matrix.append({
                    "day_index": d_idx,
                    "day_name": day_name,
                    "hour": hr,
                    "count": cnt
                })
        return matrix
