from typing import Dict, Any, List
import pandas as pd
import numpy as np

class CorrelationAnalyzer:
    """Computes statistical correlation matrices for accident metrics."""

    @classmethod
    def compute_correlation_matrix(cls, df: pd.DataFrame) -> Dict[str, Any]:
        if df.empty:
            return {"variables": [], "matrix": []}

        numeric_candidates = [
            "fatalities_count", "injured_count", "vehicles_involved_count",
            "hour_of_day", "year"
        ]
        available = [c for c in numeric_candidates if c in df.columns]
        if len(available) < 2:
            return {"variables": [], "matrix": []}

        num_df = df[available].apply(pd.to_numeric, errors="coerce").fillna(0)
        corr = num_df.corr(method="pearson").round(3)

        matrix = []
        for row_var in available:
            for col_var in available:
                matrix.append({
                    "var1": row_var,
                    "var2": col_var,
                    "value": float(corr.loc[row_var, col_var]) if not np.isnan(corr.loc[row_var, col_var]) else 0.0
                })

        return {
            "variables": available,
            "matrix": matrix
        }
