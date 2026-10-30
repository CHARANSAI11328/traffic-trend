"""
Dataset Validation Engine for TRAFFIC TREND Platform
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np
from src.monitoring.logger import logger

@dataclass
class ValidationReport:
    """Detailed dataset validation outcome."""
    is_valid: bool
    total_records: int
    total_columns: int
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    field_summaries: Dict[str, Dict[str, Any]] = field(default_factory=dict)


class DataValidator:
    """Validates structural and semantic rules on accident datasets."""

    @classmethod
    def validate(cls, df: pd.DataFrame) -> ValidationReport:
        """Runs validation battery on DataFrame."""
        errors = []
        warnings = []
        field_summaries = {}

        if df is None or df.empty:
            return ValidationReport(
                is_valid=False,
                total_records=0,
                total_columns=0,
                errors=["Dataset is empty or could not be loaded."],
                warnings=[]
            )

        n_records = len(df)
        n_cols = len(df.columns)

        # 1. Minimum record requirement
        if n_records < 5:
            warnings.append(f"Low sample size: Dataset contains only {n_records} records.")

        # 2. Date presence check
        date_candidates = ["accident_date", "date", "incident_date"]
        date_col = next((c for c in date_candidates if c in df.columns), None)
        if not date_col:
            warnings.append("No explicit date column identified. Time-series features will be limited.")
        else:
            invalid_dates = pd.to_datetime(df[date_col], errors="coerce").isna().sum()
            if invalid_dates > 0:
                warnings.append(f"{invalid_dates} records ({invalid_dates/n_records*100:.1f}%) contain unparseable dates.")

        # 3. Severity column check
        severity_candidates = ["accident_severity", "severity", "crash_severity"]
        sev_col = next((c for c in severity_candidates if c in df.columns), None)
        if not sev_col:
            warnings.append("No severity column found. Severity analysis will fall back to casualty counts.")

        # 4. Casualty counts check
        for c_col in ["fatalities_count", "injured_count"]:
            if c_col in df.columns:
                non_num = pd.to_numeric(df[c_col], errors="coerce").isna().sum()
                if non_num > 0:
                    warnings.append(f"Column '{c_col}' has {non_num} non-numeric entries.")

        # 5. Coordinate checks
        if "latitude" in df.columns and "longitude" in df.columns:
            lats = pd.to_numeric(df["latitude"], errors="coerce")
            lons = pd.to_numeric(df["longitude"], errors="coerce")
            invalid_lats = ((lats < -90) | (lats > 90)).sum()
            invalid_lons = ((lons < -180) | (lons > 180)).sum()
            if invalid_lats > 0 or invalid_lons > 0:
                warnings.append(f"Out of boundary coordinates detected: {invalid_lats} latitudes, {invalid_lons} longitudes.")

        # Per-column summaries
        for col in df.columns:
            s = df[col]
            null_count = int(s.isna().sum())
            field_summaries[col] = {
                "dtype": str(s.dtype),
                "null_count": null_count,
                "null_pct": round((null_count / n_records) * 100, 2),
                "distinct_count": int(s.nunique(dropna=True))
            }

        is_valid = len(errors) == 0
        return ValidationReport(
            is_valid=is_valid,
            total_records=n_records,
            total_columns=n_cols,
            errors=errors,
            warnings=warnings,
            field_summaries=field_summaries
        )

