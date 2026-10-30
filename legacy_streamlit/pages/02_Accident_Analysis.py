"""
Module B — Accident Exploration & Contributing Factor Analysis
TRAFFIC TREND — Road Accident Data Analysis & Intelligence Platform
"""
import streamlit as st
import pandas as pd
from src.components.theme import inject_custom_theme, render_brand_header
from src.components.cards import render_kpi_card, render_filter_summary
from src.components.charts import (
    create_bar_chart, create_donut_chart, create_time_series_chart
)
from src.analytics.severity import SeverityAnalyzer
from src.analytics.trends import TrendAnalyzer
from src.utils.state import get_current_data, render_sidebar_filters

st.set_page_config(page_title="Accident Analysis | TRAFFIC TREND", page_icon="💥", layout="wide")
inject_custom_theme()

render_brand_header(
    title="Module B: Accident Exploration & Etiology",
    subtitle="Collision Types, Contributing Human Violations, Road Surface Conditions, and Vehicle Modalities"
)

raw_df, enriched_df = get_current_data()
if enriched_df.empty:
    st.warning("No active dataset loaded.")
    st.stop()

filtered_df, active_filters = render_sidebar_filters(enriched_df)
render_filter_summary(len(filtered_df), len(enriched_df), active_filters)

# Visual Grid
tab_col, tab_cause, tab_veh, tab_env = st.tabs([
    "💥 Collision Manners",
    "⚠️ Contributing Violations & Causes",
    "🚗 Vehicle Modalities",
    "🌧️ Environmental & Road Surface Factors"
])

with tab_col:
    col1, col2 = st.columns([7, 5])
    with col1:
        if "collision_type" in filtered_df.columns:
            col_counts = filtered_df["collision_type"].value_counts().reset_index()
            col_counts.columns = ["Collision Type", "Crashes"]
            fig_col = create_bar_chart(
                df=col_counts,
                x_col="Crashes",
                y_col="Collision Type",
                title="Crashes by Manner of Collision",
                orientation="h"
            )
            st.plotly_chart(fig_col, use_container_width=True)
        else:
            st.info("Collision type field not recorded in active dataset.")

    with col2:
        if "collision_type" in filtered_df.columns:
            fig_col_donut = create_donut_chart(
                df=col_counts,
                names_col="Collision Type",
                values_col="Crashes",
                title="Collision Type Proportional Breakdown"
            )
            st.plotly_chart(fig_col_donut, use_container_width=True)

with tab_cause:
    c_cause1, c_cause2 = st.columns([7, 5])
    with c_cause1:
        factor_col = next((c for c in ["contributing_factor", "cause", "accident_cause"] if c in filtered_df.columns), None)
        if factor_col:
            factor_df = filtered_df[factor_col].value_counts().reset_index()
            factor_df.columns = ["Primary Cause", "Crashes"]
            fig_cause = create_bar_chart(
                df=factor_df,
                x_col="Crashes",
                y_col="Primary Cause",
                title="Primary Contributing Factor / Violation",
                orientation="h",
                color="#f97316"
            )
            st.plotly_chart(fig_cause, use_container_width=True)
        else:
            st.info("Contributing factor or cause column not found.")

    with c_cause2:
        if factor_col:
            st.markdown("#### 🔍 Cause Morbidity & Mortality")
            cause_morb = filtered_df.groupby(factor_col).agg(
                Crashes=("accident_id" if "accident_id" in filtered_df.columns else factor_col, "count"),
                Fatalities=("fatalities_count", lambda x: pd.to_numeric(x, errors="coerce").fillna(0).sum()) if "fatalities_count" in filtered_df.columns else (factor_col, lambda x: 0),
            ).reset_index().sort_values("Fatalities", ascending=False)
            cause_morb["Death_Rate_%"] = round(cause_morb["Fatalities"] / cause_morb["Crashes"] * 100, 1)
            st.dataframe(cause_morb, hide_index=True, use_container_width=True)

with tab_veh:
    v_col1, v_col2 = st.columns([7, 5])
    with v_col1:
        veh_df = SeverityAnalyzer.analyze_by_vehicle_type(filtered_df)
        if not veh_df.empty:
            fig_veh = create_bar_chart(
                df=veh_df,
                x_col="total_accidents",
                y_col="primary_vehicle_type",
                title="Crash Frequency by Vehicle Category",
                orientation="h",
                color="#38bdf8"
            )
            st.plotly_chart(fig_veh, use_container_width=True)
        else:
            st.info("Primary vehicle type column not available.")

    with v_col2:
        if not veh_df.empty:
            st.markdown("#### 🚨 Vulnerable Road User Vulnerability")
            st.dataframe(
                veh_df[["primary_vehicle_type", "total_accidents", "fatalities", "fatality_rate_pct"]].rename(
                    columns={"primary_vehicle_type": "Vehicle Type", "total_accidents": "Crashes", "fatalities": "Fatalities", "fatality_rate_pct": "Fatality Rate %"}
                ),
                hide_index=True,
                use_container_width=True
            )

with tab_env:
    e_col1, e_col2 = st.columns(2)
    env_data = SeverityAnalyzer.analyze_by_road_and_weather(filtered_df)
    
    with e_col1:
        if "road_type" in env_data:
            fig_road = create_bar_chart(
                df=env_data["road_type"],
                x_col="total_accidents",
                y_col="road_type",
                title="Accidents by Road Classification",
                orientation="h"
            )
            st.plotly_chart(fig_road, use_container_width=True)
        else:
            st.info("Road classification column not found.")

    with e_col2:
        if "weather" in env_data:
            fig_weath = create_bar_chart(
                df=env_data["weather"],
                x_col="total_accidents",
                y_col="weather",
                title="Accidents by Atmospheric Weather Condition",
                orientation="h",
                color="#818cf8"
            )
            st.plotly_chart(fig_weath, use_container_width=True)
        else:
            st.info("Weather condition column not found.")

