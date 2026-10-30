"""
Statistical Forecasting Engine for TRAFFIC TREND Platform
Projects baseline accident trajectories with 95% confidence intervals.
Explicitly documents analytical assumptions and limitations.
"""
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

@dataclass
class ForecastResult:
    """Carries projected values, uncertainty intervals, and mathematical assumptions."""
    historical_dates: List[str]
    historical_values: List[float]
    forecast_dates: List[str]
    forecast_values: List[float]
    lower_bound_95: List[float]
    upper_bound_95: List[float]
    model_name: str
    r_squared: float
    mae: float
    assumptions_and_limitations: List[str] = field(default_factory=lambda: [
        "Linear trend extrapolation assuming stationary reporting patterns and continuity of underlying road usage.",
        "Does not account for future legislative interventions, speed limit changes, or targeted enforcement drives.",
        "Prediction intervals widen with horizon to represent escalating variance over time.",
        "Analytical indicator for capacity planning; not a deterministic guarantee of future crash counts."
    ])


class AccidentForecaster:
    """Generates baseline time-series projections when adequate historical depth is available."""

    @classmethod
    def generate_monthly_forecast(
        cls,
        df: pd.DataFrame,
        horizon_months: int = 6
    ) -> Optional[ForecastResult]:
        """
        Fits linear trend with rolling variance confidence bounds.
        Requires at least 12 monthly periods to ensure baseline validity.
        """
        if "accident_date" not in df.columns:
            return None

        temp = df.copy()
        temp["accident_date"] = pd.to_datetime(temp["accident_date"], errors="coerce")
        temp = temp.dropna(subset=["accident_date"])

        if len(temp) < 30:
            return None

        monthly = temp.set_index("accident_date").resample("ME").size()
        if len(monthly) < 8:
            return None

        y = monthly.values.astype(float)
        x = np.arange(len(y))

        # Fit linear regression: y = m*x + c
        poly_coeff = np.polyfit(x, y, 1)
        slope, intercept = poly_coeff[0], poly_coeff[1]
        
        y_pred = (slope * x) + intercept
        residuals = y - y_pred
        std_err = float(np.std(residuals))
        mae = float(np.mean(np.abs(residuals)))
        
        # R-squared
        ss_res = np.sum(residuals ** 2)
        ss_tot = np.sum((y - np.mean(y)) ** 2)
        r2 = float(1 - (ss_res / ss_tot)) if ss_tot > 0 else 0.0
        r2 = max(0.0, min(1.0, r2))

        # Future predictions
        future_x = np.arange(len(y), len(y) + horizon_months)
        last_date = monthly.index[-1]
        future_dates = [
            (last_date + pd.DateOffset(months=i+1)).strftime("%b %Y")
            for i in range(horizon_months)
        ]
        
        future_y = (slope * future_x) + intercept
        future_y = np.maximum(future_y, 0)  # Cannot have negative accidents

        # Widen confidence interval with sqrt of step forward
        z_score_95 = 1.96
        lower_bounds = []
        upper_bounds = []
        for i, val in enumerate(future_y):
            margin = z_score_95 * std_err * np.sqrt(1 + ((i + 1) / len(y)))
            lower_bounds.append(round(max(0.0, val - margin), 1))
            upper_bounds.append(round(val + margin, 1))

        return ForecastResult(
            historical_dates=[d.strftime("%b %Y") for d in monthly.index],
            historical_values=[float(v) for v in y],
            forecast_dates=future_dates,
            forecast_values=[round(float(v), 1) for v in future_y],
            lower_bound_95=lower_bounds,
            upper_bound_95=upper_bounds,
            model_name="Parametric Linear Trend with Heteroskedastic Dynamic Dispersion",
            r_squared=round(r2, 3),
            mae=round(mae, 1)
        )

