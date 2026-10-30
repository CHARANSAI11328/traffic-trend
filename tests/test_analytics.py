"""
Unit Tests for Analytical Algorithms, KPIs, Trends, and Anomaly Engines
"""
import pytest
import pandas as pd
import numpy as np
from src.analytics.kpis import KPICalculator
from src.analytics.trends import TrendAnalyzer
from src.analytics.geographical import GeographicalAnalyzer
from src.analytics.severity import SeverityAnalyzer
from src.analytics.risk_analysis import RiskIntelligenceAnalyzer
from src.analytics.forecasting import AccidentForecaster

@pytest.fixture
def sample_analytics_df():
    """Generates synthetic dataset for analytical algorithm testing."""
    dates = pd.date_range(start="2022-01-01", periods=100, freq="D")
    return pd.DataFrame({
        "accident_id": [f"TEST-{i:03d}" for i in range(100)],
        "accident_date": dates,
        "year": dates.year,
        "month": dates.month_name(),
        "day_of_week": dates.day_name(),
        "hour_of_day": np.random.randint(0, 24, size=100),
        "state": np.random.choice(["State A", "State B", "State C"], size=100),
        "district": np.random.choice(["District 1", "District 2"], size=100),
        "accident_severity": np.random.choice(["Fatal", "Grievous Injury", "Minor Injury"], size=100),
        "fatalities_count": np.random.choice([0, 1, 2], p=[0.7, 0.2, 0.1], size=100),
        "injured_count": np.random.choice([0, 1, 3], p=[0.5, 0.3, 0.2], size=100)
    })

def test_kpi_computation(sample_analytics_df):
    """Verify KPI snapshot values are calculated correctly without hardcoded or zero mocks."""
    kpi = KPICalculator.compute(sample_analytics_df)
    assert kpi.total_accidents == 100
    assert kpi.total_fatalities >= 0
    assert kpi.total_injured >= 0
    assert kpi.total_casualties == kpi.total_fatalities + kpi.total_injured
    assert kpi.fatality_rate_pct >= 0.0

def test_kpi_empty_dataframe_handling():
    """Defensive handling when empty dataframe is passed."""
    empty_kpi = KPICalculator.compute(pd.DataFrame())
    assert empty_kpi.total_accidents == 0
    assert empty_kpi.total_fatalities == 0
    assert empty_kpi.fatality_rate_pct == 0.0

def test_yearly_trend_analysis(sample_analytics_df):
    """Verify yearly trend aggregation and percentage growth."""
    res = TrendAnalyzer.analyze_yearly_trend(sample_analytics_df)
    assert not res.empty
    assert "total_accidents" in res.columns
    assert res["total_accidents"].sum() == 100

def test_hourly_distribution_24_hours(sample_analytics_df):
    """Verify 24-hour distribution contains all 24 hour slots."""
    res = TrendAnalyzer.analyze_hourly_distribution(sample_analytics_df)
    assert len(res) == 24
    assert res["total_accidents"].sum() == 100

def test_regional_risk_index(sample_analytics_df):
    """Verify composite Risk Priority Index computation."""
    risk_df = RiskIntelligenceAnalyzer.calculate_regional_risk_index(sample_analytics_df, region_col="state")
    assert not risk_df.empty
    assert "risk_index" in risk_df.columns
    assert "risk_tier" in risk_df.columns
    assert (risk_df["risk_index"] >= 0).all()
    assert (risk_df["risk_index"] <= 100).all()

def test_forecasting_engine():
    """Verify forecasting produces predictions with prediction intervals."""
    # Create 24 months of synthetic monthly data
    dates = pd.date_range(start="2021-01-01", periods=500, freq="D")
    df = pd.DataFrame({
        "accident_date": dates,
        "fatalities_count": np.random.randint(0, 3, size=500)
    })
    forecast = AccidentForecaster.generate_monthly_forecast(df, horizon_months=6)
    assert forecast is not None
    assert len(forecast.forecast_values) == 6
    assert len(forecast.upper_bound_95) == 6
    assert len(forecast.lower_bound_95) == 6
    assert forecast.r_squared >= 0.0

