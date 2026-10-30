"""
Module F — Risk Intelligence, Anomaly Detection & Forecasting
TRAFFIC TREND — Road Accident Data Analysis & Intelligence Platform
"""
import streamlit as st
import pandas as pd
from src.components.theme import inject_custom_theme, render_brand_header
from src.components.cards import render_kpi_card, render_filter_summary
from src.components.charts import (
    create_bar_chart, create_forecast_plot, create_correlation_heatmap
)
from src.analytics.risk_analysis import RiskIntelligenceAnalyzer
from src.analytics.forecasting import AccidentForecaster
from src.analytics.correlations import CorrelationAnalyzer
from src.utils.state import get_current_data, render_sidebar_filters

st.set_page_config(page_title="Risk Intelligence | TRAFFIC TREND", page_icon="⚡", layout="wide")
inject_custom_theme()

render_brand_header(
    title="Module F: Risk Intelligence, Anomalies & Statistical Projections",
    subtitle="Composite Risk Priority Indexing, Z-Score Anomaly Detection, and Parametric Trajectory Forecasting"
)

raw_df, enriched_df = get_current_data()
if enriched_df.empty:
    st.warning("No active dataset loaded.")
    st.stop()

filtered_df, active_filters = render_sidebar_filters(enriched_df)
render_filter_summary(len(filtered_df), len(enriched_df), active_filters)

# Methodology Banner Alert
st.markdown("""
<div style="background-color: #161b22; border-left: 4px solid #38bdf8; padding: 0.8rem 1.2rem; border-radius: 4px; margin-bottom: 1.25rem;">
    <b style="color: #38bdf8;">Statistical Methodology & Integrity Notice:</b>
    <span style="color: #94a3b8; font-size: 0.85rem;">
    Risk scores and forecast curves are purely empirical analytical indicators designed for priority resource allocation. 
    They do not represent deterministic guarantees of future events. In accordance with rigorous scientific practices, 
    observed correlations between variables indicate statistical associations and do NOT prove causality.
    </span>
</div>
""", unsafe_allow_html=True)

risk_tab1, risk_tab2, risk_tab3, risk_tab4 = st.tabs([
    "🎯 Regional Risk Priority Index",
    "🚨 Statistical Anomaly Detection",
    "📈 Baseline Trajectory Forecasting",
    "🔗 Correlation Matrix & Associations"
])

with risk_tab1:
    st.markdown("#### ⚖️ Composite Regional Risk Index (RPI)")
    st.caption("RPI blends normalized crash volume (40% weight) with fatality mortality rate (60% weight).")
    
    risk_df = RiskIntelligenceAnalyzer.calculate_regional_risk_index(filtered_df, region_col="state")
    if not risk_df.empty:
        r_col1, r_col2 = st.columns([7, 5])
        with r_col1:
            fig_risk = create_bar_chart(
                df=risk_df.head(10),
                x_col="risk_index",
                y_col="state",
                title="Top 10 Highest Risk Jurisdictions (Composite 0-100 Score)",
                orientation="h",
                color="#ef4444"
            )
            st.plotly_chart(fig_risk, use_container_width=True)

        with r_col2:
            st.markdown("#### 📋 Prioritization Matrix")
            st.dataframe(
                risk_df[["state", "risk_index", "risk_tier", "total_accidents", "fatality_rate_pct"]].rename(
                    columns={
                        "state": "Jurisdiction",
                        "risk_index": "Risk Index",
                        "risk_tier": "Priority Tier",
                        "total_accidents": "Crashes",
                        "fatality_rate_pct": "Fatality %"
                    }
                ),
                hide_index=True,
                use_container_width=True
            )
    else:
        st.info("Insufficient regional dimensions to compute Risk Priority Index.")

with risk_tab2:
    st.markdown("#### 🔍 Statistical Volume Surge Detection (Z-Score Outliers)")
    st.caption("Identifies calendar months or periods where accident volume deviates significantly from baseline (|Z| ≥ 2.0).")
    
    anomalies = RiskIntelligenceAnalyzer.detect_temporal_anomalies(filtered_df, freq="ME", z_threshold=2.0)
    if anomalies:
        for a in anomalies:
            badge_cls = "badge-critical" if a.severity_level == "CRITICAL" else "badge-warning"
            st.markdown(f"""
            <div style="background-color: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 0.8rem 1.2rem; margin-bottom: 0.6rem;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <b style="color: #f0f6fc; font-size: 0.95rem;">📅 Period: {a.entity_name}</b>
                    <span class="{badge_cls}">{a.severity_level} (Z = {a.z_score})</span>
                </div>
                <div style="color: #94a3b8; font-size: 0.85rem; margin-top: 4px;">
                    {a.description} | Baseline historical mean: {a.baseline_mean} (σ = {a.std_deviation})
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.success("✅ No statistical anomalies (Z ≥ 2.0) detected in the current filtered time horizon.")

with risk_tab3:
    st.markdown("#### 📈 Longitudinal Time-Series Projection")
    st.caption("Parametric linear extrapolation with heteroskedastic 95% confidence bounds.")
    
    horizon = st.slider("Forecast Horizon (Months Ahead):", min_value=3, max_value=12, value=6, step=1)
    forecast_res = AccidentForecaster.generate_monthly_forecast(filtered_df, horizon_months=horizon)
    
    if forecast_res:
        fig_fc = create_forecast_plot(forecast_res, title=f"{horizon}-Month Projected Trajectory with 95% Confidence Bounds")
        st.plotly_chart(fig_fc, use_container_width=True)
        
        st.markdown("##### 📐 Mathematical Assumptions & Scientific Bounds")
        for assumption in forecast_res.assumptions_and_limitations:
            st.markdown(f"- ℹ️ *{assumption}*")
            
        st.caption(f"Model goodness-of-fit: $R^2 = {forecast_res.r_squared}$ | Mean Absolute Error (MAE): {forecast_res.mae} incidents")
    else:
        st.info("Forecasting requires at least 8 continuous monthly periods with sufficient record depth.")

with risk_tab4:
    st.markdown("#### 🔗 Numerical Indicator Correlation Matrix")
    corr_df = CorrelationAnalyzer.compute_numeric_correlations(filtered_df)
    if not corr_df.empty:
        fig_corr = create_correlation_heatmap(corr_df, title="Pearson Correlation Coefficients")
        st.plotly_chart(fig_corr, use_container_width=True)
    else:
        st.info("Insufficient numeric indicators to construct a bivariate correlation matrix.")

