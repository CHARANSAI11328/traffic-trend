"""
Data Quality Profiler and Scorecard Calculator for TRAFFIC TREND Platform
Provides mathematical, documented quality metrics across 4 key dimensions:
Completeness, Uniqueness, Validity, and Consistency.
"""
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
        """Calculates four-dimensional quality indices."""
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
        invalid_dates = 0
        date_col = next((c for c in ["accident_date", "date"] if c in df.columns), None)
        if date_col:
            total_validity_checks += n_rows
            invalid_dates = int(pd.to_datetime(df[date_col], errors="coerce").isna().sum())
            validity_deductions += invalid_dates

        # Coordinates validity check
        invalid_coords = 0
        if "latitude" in df.columns:
            total_validity_checks += n_rows
            lats = pd.to_numeric(df["latitude"], errors="coerce")
            invalid_coords += int(((lats < -90) | (lats > 90)).sum())
        if "longitude" in df.columns:
            total_validity_checks += n_rows
            lons = pd.to_numeric(df["longitude"], errors="coerce")
            invalid_coords += int(((lons < -180) | (lons > 180)).sum())
        validity_deductions += invalid_coords

        # Casualty non-negative check
        if "fatalities_count" in df.columns:
            total_validity_checks += n_rows
            fat = pd.to_numeric(df["fatalities_count"], errors="coerce").fillna(0)
            validity_deductions += int((fat < 0).sum())

        if total_validity_checks > 0:
            validity = max(0.0, min(100.0, 100.0 - (validity_deductions / total_validity_checks * 100)))
        else:
            validity = 100.0

        # 4. Consistency Calculation (Weight: 20%)
        # Rule: If severity is 'Fatal', fatalities_count should be >= 1
        # Rule: If fatalities_count >= 1, severity should not be 'Minor' or 'Property Damage Only'
        consistency = 100.0
        if "accident_severity" in df.columns and "fatalities_count" in df.columns:
            fats = pd.to_numeric(df["fatalities_count"], errors="coerce").fillna(0)
            sevs = df["accident_severity"].astype(str).str.lower()
            
            inconsistent_fatal = ((sevs == "fatal") & (fats == 0)).sum()
            inconsistent_minor = ((fats > 0) & (sevs.isin(["minor", "minor injury", "property damage only"]))).sum()
            
            inconsistencies = inconsistent_fatal + inconsistent_minor
            consistency = max(0.0, min(100.0, 100.0 - (inconsistencies / n_rows * 100)))

        # Composite Overall Score
        overall = round(
            (0.30 * completeness) +
            (0.25 * uniqueness) +
            (0.25 * validity) +
            (0.20 * consistency),
            1
        )

        if overall >= 90.0:
            grade = "A+ Excellent"
        elif overall >= 80.0:
            grade = "A Reliable"
        elif overall >= 70.0:
            grade = "B Acceptable"
        elif overall >= 55.0:
            grade = "C Fair (Needs Cleaning)"
        else:
            grade = "D Critical Quality Issues"

        # Column Profiling
        col_profiles = {}
        for col in df.columns:
            series = df[col]
            nulls = int(series.isna().sum())
            distinct = int(series.nunique(dropna=True))
            dtype = str(series.dtype)
            
            sample_vals = series.dropna().head(3).tolist()
            sample_str = [str(v) for v in sample_vals]

            col_profiles[col] = {
                "dtype": dtype,
                "null_count": nulls,
                "null_pct": round((nulls / n_rows) * 100, 1) if n_rows > 0 else 0.0,
                "distinct_count": distinct,
                "sample_values": sample_str
            }

        return QualityScorecard(
            total_records=n_rows,
            total_columns=n_cols,
            completeness_score=round(completeness, 1),
            uniqueness_score=round(uniqueness, 1),
            validity_score=round(validity, 1),
            consistency_score=round(consistency, 1),
            overall_score=overall,
            quality_grade=grade,
            duplicate_count=dup_count,
            duplicate_pct=dup_pct,
            total_missing_cells=missing_cells,
            missing_cells_pct=missing_cells_pct,
            invalid_dates_count=invalid_dates,
            invalid_coords_count=invalid_coords,
            column_profiles=col_profiles
        )

