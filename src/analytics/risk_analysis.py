"""
Risk Intelligence & Statistical Anomaly Detection Engine for TRAFFIC TREND Platform
Computes multi-dimensional risk scores, hotspot concentrations, and Z-score anomalies.
Notice: Risk scores are empirical analytical indicators, not guaranteed causal forecasts.
"""
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

@dataclass
class AnomalyEvent:
    """Represents a statistically significant deviation in crash frequency."""
    entity_name: str       # Date, Month, or Region
    observed_value: float
    baseline_mean: float
    std_deviation: float
    z_score: float
    severity_level: str    # "CRITICAL", "ELEVATED", "MODERATE"
    description: str


class RiskIntelligenceAnalyzer:
    """Calculates risk prioritization indices and identifies statistical outliers."""

    @classmethod
    def calculate_regional_risk_index(cls, df: pd.DataFrame, region_col: str = "state") -> pd.DataFrame:
        """
        Computes composite Risk Priority Index (RPI):
        RPI = (Normalized Crash Frequency * 0.40) + (Normalized Fatality Rate * 0.60) * 100
        Weights mortality higher than property damage.
        """
        if region_col not in df.columns:
            return pd.DataFrame()

        valid = df.dropna(subset=[region_col]).copy()
        valid[region_col] = valid[region_col].astype(str).str.strip()

        grouped = valid.groupby(region_col).agg(
            total_accidents=("accident_id" if "accident_id" in valid.columns else region_col, "count"),
            fatalities=("fatalities_count", lambda x: pd.to_numeric(x, errors="coerce").fillna(0).sum()) if "fatalities_count" in valid.columns else (region_col, lambda x: 0),
            injuries=("injured_count", lambda x: pd.to_numeric(x, errors="coerce").fillna(0).sum()) if "injured_count" in valid.columns else (region_col, lambda x: 0),
        ).reset_index()

        if grouped.empty or len(grouped) < 2:
            return grouped

        grouped["fatality_rate_pct"] = (grouped["fatalities"] / grouped["total_accidents"].replace(0, np.nan)).fillna(0) * 100.0

        # Min-Max Normalization (0.0 to 1.0)
        acc_min, acc_max = grouped["total_accidents"].min(), grouped["total_accidents"].max()
        fat_rate_min, fat_rate_max = grouped["fatality_rate_pct"].min(), grouped["fatality_rate_pct"].max()

        acc_norm = (grouped["total_accidents"] - acc_min) / (acc_max - acc_min) if acc_max > acc_min else 0.5
        fat_norm = (grouped["fatality_rate_pct"] - fat_rate_min) / (fat_rate_max - fat_rate_min) if fat_rate_max > fat_rate_min else 0.5

        grouped["risk_index"] = round(((acc_norm * 0.40) + (fat_norm * 0.60)) * 100.0, 1)
        
        # Risk Category classification
        def categorize_risk(score):
            if score >= 75.0:
                return "Critical Priority"
            elif score >= 50.0:
                return "High Priority"
            elif score >= 25.0:
                return "Moderate Attention"
            else:
                return "Low Risk Baseline"

        grouped["risk_tier"] = grouped["risk_index"].apply(categorize_risk)
        return grouped.sort_values("risk_index", ascending=False).reset_index(drop=True)

    @classmethod
    def detect_temporal_anomalies(
        cls,
        df: pd.DataFrame,
        freq: str = "ME",
        z_threshold: float = 2.0
    ) -> List[AnomalyEvent]:
        """
        Detects statistical volume spikes using rolling or historical Z-score.
        z = (observed - mean) / std_dev
        z >= 2.0 corresponds to p < 0.05 (unusual surge)
        z >= 3.0 corresponds to p < 0.003 (extreme surge)
        """
        if "accident_date" not in df.columns:
            return []

        temp = df.copy()
        temp["accident_date"] = pd.to_datetime(temp["accident_date"], errors="coerce")
        temp = temp.dropna(subset=["accident_date"])

        if len(temp) < 20:
            return []

        # Resample to frequency
        series = temp.set_index("accident_date").resample(freq).size()
        if len(series) < 6:
            return []

        mean_val = float(series.mean())
        std_val = float(series.std())

        if std_val == 0:
            return []

        anomalies = []
        for dt, count in series.items():
            z = (count - mean_val) / std_val
            if z >= z_threshold:
                level = "CRITICAL" if z >= 3.0 else "ELEVATED"
                dt_str = dt.strftime("%B %Y") if freq == "ME" else dt.strftime("%Y-%m-%d")
                anomalies.append(AnomalyEvent(
                    entity_name=dt_str,
                    observed_value=float(count),
                    baseline_mean=round(mean_val, 1),
                    std_deviation=round(std_val, 1),
                    z_score=round(z, 2),
                    severity_level=level,
                    description=f"{level} volume surge: {int(count)} crashes recorded (Z={z:.2f}, baseline mean: {mean_val:.1f})"
                ))

        return sorted(anomalies, key=lambda a: a.z_score, reverse=True)

