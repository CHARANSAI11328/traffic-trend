from typing import List, Optional
import pandas as pd
import numpy as np

class DataTransformer:
    """Transforms raw accident DataFrames into canonical analytics representations."""

    @classmethod
    def transform(cls, df: pd.DataFrame) -> pd.DataFrame:
        if df is None or df.empty:
            return pd.DataFrame()

        tdf = df.copy()

        # Date transformations
        if "accident_date" in tdf.columns:
            date_dt = pd.to_datetime(tdf["accident_date"], errors="coerce")
            tdf["year"] = date_dt.dt.year
            tdf["month"] = date_dt.dt.strftime("%B")
            tdf["day_of_week"] = date_dt.dt.strftime("%A")
            tdf["is_weekend"] = date_dt.dt.dayofweek.isin([5, 6]).astype(int)

        # Time transformations
        if "accident_time" in tdf.columns and ("hour_of_day" not in tdf.columns or tdf["hour_of_day"].isna().all()):
            time_parsed = pd.to_datetime(tdf["accident_time"], format="%H:%M:%S", errors="coerce")
            tdf["hour_of_day"] = time_parsed.dt.hour

        # Numeric casts
        for col in ["fatalities_count", "injured_count", "vehicles_involved_count"]:
            if col in tdf.columns:
                tdf[col] = pd.to_numeric(tdf[col], errors="coerce").fillna(0).astype(int)

        # Computed Casualty Metrics
        if "fatalities_count" in tdf.columns and "injured_count" in tdf.columns:
            tdf["total_casualties"] = tdf["fatalities_count"] + tdf["injured_count"]
            tdf["is_fatal"] = (tdf["fatalities_count"] > 0) | (tdf.get("accident_severity", "").astype(str).str.lower().str.contains("fatal"))
            tdf["is_fatal"] = tdf["is_fatal"].astype(int)

        return tdf
