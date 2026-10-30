from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import pandas as pd
import numpy as np

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

        if n_records < 5:
            warnings.append(f"Low sample size: Dataset contains only {n_records} records.")

        date_candidates = ["accident_date", "date", "incident_date"]
        date_col = next((c for c in date_candidates if c in df.columns), None)
        if not date_col:
            warnings.append("No explicit date column identified. Time-series features will be limited.")
        else:
            invalid_dates = int(pd.to_datetime(df[date_col], errors="coerce").isna().sum())
            if invalid_dates > 0:
                warnings.append(f"{invalid_dates} records ({invalid_dates/n_records*100:.1f}%) contain unparseable dates.")

        severity_candidates = ["accident_severity", "severity", "crash_severity"]
        sev_col = next((c for c in severity_candidates if c in df.columns), None)
        if not sev_col:
            warnings.append("No explicit severity column identified. Severity analytics may be limited.")

        for c in df.columns:
            missing_c = int(df[c].isna().sum())
            field_summaries[c] = {
                "dtype": str(df[c].dtype),
                "null_count": missing_c,
                "null_pct": round((missing_c / n_records) * 100, 2)
            }

        return ValidationReport(
            is_valid=len(errors) == 0,
            total_records=n_records,
            total_columns=n_cols,
            errors=errors,
            warnings=warnings,
            field_summaries=field_summaries
        )
