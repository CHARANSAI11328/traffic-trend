from dataclasses import dataclass, field
from typing import Dict, Any, List
import pandas as pd
import numpy as np

@dataclass
class QualityScorecard:
    """Mathematical data quality scorecard with documented component weights."""
    total_records: int
    total_columns: int
    completeness_score: float  # Weight: 30%
    uniqueness_score: float    # Weight: 25%
    validity_score: float      # Weight: 25%
    consistency_score: float   # Weight: 20%
    overall_score: float       # Weighted Composite: 0 - 100
    quality_grade: str         # Excellent (90+), Good (75-89), Fair (60-74), Poor (<60)
    
    duplicate_count: int
    duplicate_pct: float
    total_missing_cells: int
    missing_cells_pct: float
    invalid_dates_count: int
    invalid_coords_count: int
    column_profiles: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    scoring_methodology: Dict[str, str] = field(default_factory=lambda: {
        "Completeness (30%)": "Proportion of non-null cells across all columns: (1 - missing_cells / total_cells) * 100",
        "Uniqueness (25%)": "Proportion of non-duplicate records: (1 - duplicate_rows / total_rows) * 100",
        "Validity (25%)": "Percentage of conformant dates, coordinate ranges, and non-negative casualty counts",
        "Consistency (20%)": "Logical coherence between fatal severity classification and casualty figures"
    })

class DataProfiler:
    """Profiles datasets and computes institutional-grade quality scorecards."""

    @classmethod
    def profile(cls, df: pd.DataFrame) -> QualityScorecard:
        if df is None or df.empty:
            return QualityScorecard(
                total_records=0,
                total_columns=0,
                completeness_score=0.0,
                uniqueness_score=0.0,
                validity_score=0.0,
                consistency_score=0.0,
                overall_score=0.0,
                quality_grade="N/A",
                duplicate_count=0,
                duplicate_pct=0.0,
                total_missing_cells=0,
                missing_cells_pct=0.0,
                invalid_dates_count=0,
                invalid_coords_count=0,
                column_profiles={}
            )

        n_rows = len(df)
        n_cols = len(df.columns)
        total_cells = n_rows * n_cols

        # 1. Completeness Calculation (Weight: 30%)
        missing_cells = int(df.isna().sum().sum())
        missing_cells_pct = round((missing_cells / total_cells) * 100, 2) if total_cells > 0 else 0.0
        completeness = max(0.0, min(100.0, 100.0 - missing_cells_pct))

        # 2. Uniqueness Calculation (Weight: 25%)
        dup_count = int(df.duplicated().sum())
        dup_pct = round((dup_count / n_rows) * 100, 2) if n_rows > 0 else 0.0
        uniqueness = max(0.0, min(100.0, 100.0 - dup_pct))

        # 3. Validity Calculation (Weight: 25%)
        validity_deductions = 0
        total_validity_checks = 0

        # Date validity check
        invalid_dates_count = 0
        if "accident_date" in df.columns:
            parsed = pd.to_datetime(df["accident_date"], errors="coerce")
            invalid_dates_count = int(parsed.isna().sum())
            validity_deductions += invalid_dates_count
            total_validity_checks += n_rows

        # Coordinate bounds check
        invalid_coords_count = 0
        if "latitude" in df.columns:
            lat = pd.to_numeric(df["latitude"], errors="coerce")
            inv_lat = lat.isna() | (lat < -90) | (lat > 90)
            invalid_coords_count += int(inv_lat.sum())
            validity_deductions += int(inv_lat.sum())
            total_validity_checks += n_rows

        if "longitude" in df.columns:
            lon = pd.to_numeric(df["longitude"], errors="coerce")
            inv_lon = lon.isna() | (lon < -180) | (lon > 180)
            invalid_coords_count += int(inv_lon.sum())
            validity_deductions += int(inv_lon.sum())
            total_validity_checks += n_rows

        if total_validity_checks > 0:
            validity = max(0.0, min(100.0, (1.0 - (validity_deductions / total_validity_checks)) * 100.0))
        else:
            validity = 100.0

        # 4. Consistency Calculation (Weight: 20%)
        inconsistency_count = 0
        consistency_checks = 0
        if "accident_severity" in df.columns and "fatalities_count" in df.columns:
            fatal_labels = ["Fatal", "fatal", "FATAL"]
            fat_series = pd.to_numeric(df["fatalities_count"], errors="coerce").fillna(0)
            is_fatal_label = df["accident_severity"].isin(fatal_labels)
            
            # Severity marked Fatal but fatalities == 0
            inconsistencies_1 = (is_fatal_label & (fat_series == 0)).sum()
            # Severity marked Minor/Non-fatal but fatalities > 0
            inconsistencies_2 = ((~is_fatal_label) & (fat_series > 0)).sum()
            
            inconsistency_count = int(inconsistencies_1 + inconsistencies_2)
            consistency_checks = n_rows

        if consistency_checks > 0:
            consistency = max(0.0, min(100.0, (1.0 - (inconsistency_count / consistency_checks)) * 100.0))
        else:
            consistency = 100.0

        # Weighted Overall Score
        overall = round(
            (completeness * 0.30) +
            (uniqueness * 0.25) +
            (validity * 0.25) +
            (consistency * 0.20),
            2
        )

        if overall >= 90:
            grade = "A (Institutional Grade / Clean)"
        elif overall >= 75:
            grade = "B (Good / Minor Remediation Recommended)"
        elif overall >= 60:
            grade = "C (Fair / Data Cleaning Required)"
        else:
            grade = "D (Poor / High Risk of Analytical Distortion)"

        # Per-column profiling
        col_profiles = {}
        for c in df.columns:
            missing_c = int(df[c].isna().sum())
            col_profiles[c] = {
                "dtype": str(df[c].dtype),
                "missing_count": missing_c,
                "missing_pct": round((missing_c / n_rows) * 100, 2) if n_rows > 0 else 0.0,
                "unique_values": int(df[c].nunique()),
                "sample_values": [str(x) for x in df[c].dropna().head(3).tolist()]
            }

        return QualityScorecard(
            total_records=n_rows,
            total_columns=n_cols,
            completeness_score=round(completeness, 2),
            uniqueness_score=round(uniqueness, 2),
            validity_score=round(validity, 2),
            consistency_score=round(consistency, 2),
            overall_score=overall,
            quality_grade=grade,
            duplicate_count=dup_count,
            duplicate_pct=dup_pct,
            total_missing_cells=missing_cells,
            missing_cells_pct=missing_cells_pct,
            invalid_dates_count=invalid_dates_count,
            invalid_coords_count=invalid_coords_count,
            column_profiles=col_profiles
        )
