"""
Module D — Temporal Patterns & Time-Series Dynamics
TRAFFIC TREND — Road Accident Data Analysis & Intelligence Platform
"""
import streamlit as st
import pandas as pd
from src.components.theme import inject_custom_theme, render_brand_header
from src.components.cards import render_kpi_card, render_filter_summary
from src.components.charts import (
    create_time_series_chart, create_bar_chart, create_donut_chart
)
from src.analytics.trends import TrendAnalyzer
from src.utils.state import get_current_data, render_sidebar_filters

st.set_page_config(page_title="Temporal Analysis | TRAFFIC TREND", page_icon="⏱️", layout="wide")
inject_custom_theme()

render_brand_header(
    title="Module D: Temporal Dynamics & Diurnal Patterns",
    subtitle="Longitudinal Fluctuations, 24-Hour Diurnal Curves, Weekday/Weekend Variance, and Rolling Averages"
)

raw_df, enriched_df = get_current_data()
if enriched_df.empty:
    st.warning("No active dataset loaded.")
    st.stop()

filtered_df, active_filters = render_sidebar_filters(enriched_df)
render_filter_summary(len(filtered_df), len(enriched_df), active_filters)

time_tab1, time_tab2, time_tab3, time_tab4 = st.tabs([
    "📈 Rolling Moving Averages",
    "🕒 24-Hour Diurnal Curve",
    "📅 Day-of-Week & Weekend Split",
    "🗓️ Monthly Seasonality"
])

with time_tab1:
    st.markdown("#### 🌊 Daily Crash Trajectory & Rolling Moving Average")
    window_choice = st.slider("Select Moving Average Window (Days):", min_value=3, max_value=30, value=7, step=1)
    ma_df = TrendAnalyzer.compute_moving_averages(filtered_df, window=window_choice)
    if not ma_df.empty:
        fig_ma = create_time_series_chart(
            df=ma_df,
            x_col="date",
            y_cols=["daily_accidents", f"ma_{window_choice}d"],
            title=f"Daily Incident Volume with {window_choice}-Day Moving Average Smoothing",
            labels=["Daily Incidents", f"{window_choice}-Day Moving Avg"],
            colors_list=["#38bdf8", "#f43f5e"]
        )
        st.plotly_chart(fig_ma, use_container_width=True)
    else:
        st.info("Daily time-series analysis requires a valid 'accident_date' column.")

with time_tab2:
    h_col1, h_col2 = st.columns([8, 4])
    hourly_df = TrendAnalyzer.analyze_hourly_distribution(filtered_df)
    with h_col1:
        if not hourly_df.empty:
            fig_h = create_bar_chart(
                df=hourly_df,
                x_col="hour_label",
                y_col="total_accidents",
                title="Accident Volume by Hour of Day (00:00 - 23:00)",
                color="#38bdf8"
            )
            st.plotly_chart(fig_h, use_container_width=True)
        else:
            st.info("Hourly timestamp data not present.")

    with h_col2:
        st.markdown("#### ⏳ Peak Collision Windows")
        if "time_window" in filtered_df.columns:
            tw_counts = filtered_df["time_window"].value_counts().reset_index()
            tw_counts.columns = ["Window", "Crashes"]
            fig_tw = create_donut_chart(
                df=tw_counts,
                names_col="Window",
                values_col="Crashes",
                title="Distribution Across Diurnal Windows"
            )
            st.plotly_chart(fig_tw, use_container_width=True)

with time_tab3:
    d_col1, d_col2 = st.columns([7, 5])
    dow_df = TrendAnalyzer.analyze_day_of_week(filtered_df)
    with d_col1:
        if not dow_df.empty:
            fig_dow = create_bar_chart(
                df=dow_df,
                x_col="day_of_week",
                y_col="total_accidents",
                title="Crashes by Day of Week (Monday - Sunday)",
                color="#818cf8"
            )
            st.plotly_chart(fig_dow, use_container_width=True)
        else:
            st.info("Day of week dimension not found.")

    with d_col2:
        st.markdown("#### 🏖️ Weekday vs Weekend Comparison")
        if "day_type" in filtered_df.columns:
            day_type_df = filtered_df.groupby("day_type").agg(
                Crashes=("accident_id" if "accident_id" in filtered_df.columns else "day_type", "count"),
                Fatalities=("fatalities_count", lambda x: pd.to_numeric(x, errors="coerce").fillna(0).sum()) if "fatalities_count" in filtered_df.columns else ("day_type", lambda x: 0)
            ).reset_index()
            fig_dt = create_donut_chart(
                df=day_type_df,
                names_col="day_type",
                values_col="Crashes",
                title="Weekday vs Weekend Proportion"
            )
            st.plotly_chart(fig_dt, use_container_width=True)

with time_tab4:
    m_col1, m_col2 = st.columns([8, 4])
    monthly_df = TrendAnalyzer.analyze_monthly_trend(filtered_df)
    with m_col1:
        if not monthly_df.empty:
            fig_m = create_bar_chart(
                df=monthly_df,
                x_col="month",
                y_col="total_accidents",
                title="Seasonal Accident Volume by Month (Jan - Dec)",
                color="#2dd4bf"
            )
            st.plotly_chart(fig_m, use_container_width=True)
        else:
            st.info("Month column not available.")

    with m_col2:
        st.markdown("#### 📋 Monthly Distribution Table")
        if not monthly_df.empty:
            st.dataframe(monthly_df.rename(columns={"month": "Month", "total_accidents": "Crashes", "fatalities": "Deaths", "injuries": "Injured"}), hide_index=True, use_container_width=True)

