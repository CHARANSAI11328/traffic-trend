from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

class AnomalyDetector:
    """Detects statistically significant spikes in crash frequencies and casualties."""

    @classmethod
    def detect_regional_spikes(cls, df: pd.DataFrame, z_threshold: float = 1.96) -> List[Dict[str, Any]]:
        """Identifies administrative regions with accident counts exceeding statistical norms."""
        if "state" not in df.columns or df.empty:
            return []

        counts = df["state"].value_counts().reset_index()
        counts.columns = ["state", "accident_count"]

        mean_val = counts["accident_count"].mean()
        std_val = counts["accident_count"].std()

        if std_val == 0 or np.isnan(std_val):
            return []

        counts["z_score"] = ((counts["accident_count"] - mean_val) / std_val).round(2)
        
        # IQR threshold
        q25 = counts["accident_count"].quantile(0.25)
        q75 = counts["accident_count"].quantile(0.75)
        iqr = q75 - q25
        iqr_upper = q75 + (1.5 * iqr)

        counts["is_z_anomaly"] = counts["z_score"] > z_threshold
        counts["is_iqr_outlier"] = counts["accident_count"] > iqr_upper

        anomalies = []
        for _, row in counts[counts["is_z_anomaly"] | counts["is_iqr_outlier"]].iterrows():
            anomalies.append({
                "entity": row["state"],
                "metric": "Accident Volume",
                "observed_value": int(row["accident_count"]),
                "expected_mean": round(float(mean_val), 1),
                "z_score": float(row["z_score"]),
                "classification": "High Frequency Outlier",
                "methodology": f"Z-Score ({row['z_score']} > {z_threshold}) & Tukey IQR Outlier fence (> {round(iqr_upper, 1)})",
                "analytical_note": "Identifies elevated volume. Historical volume alone does not prove higher per-capita risk without exposure data."
            })

        return anomalies

    @classmethod
    def detect_fatality_spikes(cls, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Identifies districts with disproportionately elevated fatality rates."""
        if "district" not in df.columns or "fatalities_count" not in df.columns or df.empty:
            return []

        grouped = df.groupby("district").agg(
            crashes=("accident_id" if "accident_id" in df.columns else "district", "count"),
            fatalities=("fatalities_count", lambda x: pd.to_numeric(x, errors="coerce").fillna(0).sum())
        ).reset_index()

        # Minimum sample size to prevent small-number noise
        grouped = grouped[grouped["crashes"] >= 10].copy()
        if grouped.empty:
            return []

        grouped["fatality_rate"] = (grouped["fatalities"] / grouped["crashes"]) * 100.0
        mean_rate = grouped["fatality_rate"].mean()
        std_rate = grouped["fatality_rate"].std()

        if std_rate == 0 or np.isnan(std_rate):
            return []

        grouped["z_score"] = ((grouped["fatality_rate"] - mean_rate) / std_rate).round(2)
        outliers = grouped[grouped["z_score"] >= 1.75].sort_values("z_score", ascending=False)

        results = []
        for _, r in outliers.iterrows():
            results.append({
                "entity": r["district"],
                "metric": "Fatality Rate per 100 Crashes",
                "observed_value": round(float(r["fatality_rate"]), 2),
                "expected_mean": round(float(mean_rate), 2),
                "z_score": float(r["z_score"]),
                "total_crashes": int(r["crashes"]),
                "fatalities": int(r["fatalities"]),
                "classification": "Severity Concentration Spike",
                "methodology": f"Parametric Z-Score test on fatality ratios among districts with >= 10 crashes",
                "analytical_note": "Indicates high impact severity. Further road safety audit recommended for high-speed highway intersections."
            })
        return results
