"""
Statistical Correlation Engine for TRAFFIC TREND Platform
Analyzes continuous Pearson / Spearman correlations and categorical associations.
Strictly adheres to scientific guidelines: Correlation does NOT imply causation.
"""
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

class CorrelationAnalyzer:
    """Computes bivariate associations and statistical correlation matrices."""

    @classmethod
    def compute_numeric_correlations(cls, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculates Pearson correlation matrix across available numerical indicators.
        Returns correlation DataFrame or empty if insufficient numeric columns.
        """
        numeric_cols = [
            c for c in ["fatalities_count", "injured_count", "vehicles_involved_count", "hour_of_day", "casualty_severity_index"]
            if c in df.columns
        ]
        
        if len(numeric_cols) < 2:
            return pd.DataFrame()

        clean_num = df[numeric_cols].apply(pd.to_numeric, errors="coerce").dropna()
        if len(clean_num) < 10:
            return pd.DataFrame()

        corr_matrix = clean_num.corr(method="pearson").round(3)
        return corr_matrix

    @classmethod
    def compute_contingency_table(
        cls,
        df: pd.DataFrame,
        col1: str,
        col2: str
    ) -> pd.DataFrame:
        """Computes cross-tabulation frequency matrix between two categorical variables."""
        if col1 not in df.columns or col2 not in df.columns:
            return pd.DataFrame()

        clean = df[[col1, col2]].dropna()
        if clean.empty:
            return pd.DataFrame()

        ct = pd.crosstab(clean[col1], clean[col2], margins=False)
        return ct

