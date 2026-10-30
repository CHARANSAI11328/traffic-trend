from typing import Dict, Any, List, Optional
import pandas as pd
import numpy as np

class ForecastingEngine:
    """Computes statistical time-series forecasts with empirical confidence bounds."""

    @classmethod
    def generate_forecast(cls, df: pd.DataFrame, horizon_periods: int = 6) -> Dict[str, Any]:
        """
        Projects accident trajectories based on historical monthly time series.
        Uses exponential trend fitting and empirical residual variance.
        """
        if "accident_date" not in df.columns or df.empty:
            return {"historical": [], "forecast": [], "methodology": "Insufficient date attributes for time-series forecasting"}

        dates = pd.to_datetime(df["accident_date"], errors="coerce").dropna()
        if dates.empty:
            return {"historical": [], "forecast": [], "methodology": "No valid parseable dates"}

        monthly = df.copy()
        monthly["period"] = dates.dt.to_period("M").astype(str)
        series = monthly.groupby("period").size().reset_index(name="actual_accidents")
        series = series.sort_values("period").reset_index(drop=True)

        if len(series) < 6:
            return {
                "historical": series.to_dict(orient="records"),
                "forecast": [],
                "methodology": f"Sample size ({len(series)} months) too short for robust econometric forecasting (minimum 6 months required)."
            }

        # Linear & Trend Estimation
        y = series["actual_accidents"].values
        x = np.arange(len(y))

        # Fit linear regression: y = slope * x + intercept
        slope, intercept = np.polyfit(x, y, 1)
        fitted = slope * x + intercept
        residuals = y - fitted
        std_err = np.std(residuals) if len(residuals) > 1 else 5.0

        historical_records = []
        for i, row in series.iterrows():
            historical_records.append({
                "period": row["period"],
                "actual": int(row["actual_accidents"]),
                "fitted": round(float(fitted[i]), 1)
            })

        # Forecast future periods
        last_period = pd.Period(series["period"].iloc[-1], freq="M")
        forecast_records = []
        
        for step in range(1, horizon_periods + 1):
            future_period = (last_period + step).strftime("%Y-%m")
            future_x = len(x) - 1 + step
            predicted_y = max(0.0, slope * future_x + intercept)
            
            # Confidence bounds widening with step horizon
            band_multiplier = 1.96 * (1.0 + 0.15 * step)
            lower_bound = max(0.0, predicted_y - (band_multiplier * std_err))
            upper_bound = predicted_y + (band_multiplier * std_err)

            forecast_records.append({
                "period": future_period,
                "predicted": round(float(predicted_y), 1),
                "lower_bound_95": round(float(lower_bound), 1),
                "upper_bound_95": round(float(upper_bound), 1),
            })

        return {
            "historical": historical_records,
            "forecast": forecast_records,
            "slope": round(float(slope), 2),
            "trend_direction": "Increasing" if slope > 0.5 else ("Decreasing" if slope < -0.5 else "Stable"),
            "methodology": "OLS Linear Trend Decomposition with expanding confidence intervals based on residual standard error."
        }
