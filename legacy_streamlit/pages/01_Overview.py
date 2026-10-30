"""
Module A — Executive Overview Dashboard
TRAFFIC TREND — Road Accident Data Analysis & Intelligence Platform
"""
import streamlit as st
import pandas as pd
from src.components.theme import inject_custom_theme, render_brand_header
from src.components.cards import render_kpi_card, render_filter_summary
from src.components.charts import (
    create_time_series_chart, create_bar_chart, create_donut_chart
)
from src.analytics.kpis import KPICalculator
from src.analytics.trends import TrendAnalyzer
from src.analytics.geographical import GeographicalAnalyzer
from src.analytics.severity import SeverityAnalyzer
from src.utils.state import get_current_data, render_sidebar_filters

st.set_page_config(page_title="Executive Overview | TRAFFIC TREND", page_icon="🚦", layout="wide")
inject_custom_theme()

render_brand_header(
    title="Module A: Executive Overview",
    subtitle="High-Level KPI Intelligence, Multi-Horizon Trends, and Safety Performance Metrics"
)

raw_df, enriched_df = get_current_data()
if enriched_df.empty:
    st.warning("No active dataset loaded. Please navigate to Data Management to initialize data.")
    st.stop()

filtered_df, active_filters = render_sidebar_filters(enriched_df)
render_filter_summary(len(filtered_df), len(enriched_df), active_filters)

# Dynamic KPIs
kpis = KPICalculator.compute(filtered_df)

# Top KPI Row (6 metric cards)
k_col1, k_col2, k_col3, k_col4, k_col5, k_col6 = st.columns(6)

with k_col1:
    render_kpi_card("Total Incidents", f"{kpis.total_accidents:,}", icon="💥")
with k_col2:
    render_kpi_card("Total Fatalities", f"{kpis.total_fatalities:,}", icon="💀")
with k_col3:
    render_kpi_card("Total Injured", f"{kpis.total_injured:,}", icon="🩹")
with k_col4:
    render_kpi_card("Fatal Crashes", f"{kpis.fatal_accidents_count:,}", icon="⚠️")
with k_col5:
    render_kpi_card("Fatality Rate", f"{kpis.fatality_rate_pct:.1f}%", icon="📉")
with k_col6:
    render_kpi_card("Avg Daily Crashes", f"{kpis.avg_accidents_per_day:.1f}", icon="📅")

st.markdown("<br>", unsafe_allow_html=True)

# Main Visual Analytics
tab1, tab2, tab3 = st.tabs(["📊 Longitudinal Evolution", "🗺️ Geographic Leaders", "🚑 Severity Composition"])

with tab1:
    col1, col2 = st.columns([8, 4])
    with col1:
        yearly_df = TrendAnalyzer.analyze_yearly_trend(filtered_df)
        if not yearly_df.empty:
            fig_y = create_time_series_chart(
                df=yearly_df,
                x_col="year",
                y_cols=["total_accidents", "fatalities", "injuries"],
                title="Annual Volume: Accidents, Fatalities and Injuries",
                labels=["Accidents", "Deaths", "Injuries"]
            )
            st.plotly_chart(fig_y, use_container_width=True)
        else:
            st.info("Yearly trend requires valid 'year' or 'accident_date' column.")

    with col2:
        st.markdown("#### 📋 Annual Growth Summary")
        if not yearly_df.empty:
            display_tbl = yearly_df[["year", "total_accidents", "fatalities", "fatality_rate_pct"]].copy()
            display_tbl.columns = ["Year", "Total Crashes", "Fatalities", "Fatality Rate (%)"]
            st.dataframe(display_tbl, hide_index=True, use_container_width=True)
            
            # Download CSV
            csv = display_tbl.to_csv(index=False).encode('utf-8')
            st.download_button("⬇️ Download Annual Summary", data=csv, file_name="annual_traffic_trend_summary.csv", mime="text/csv")

with tab2:
    c_geo1, c_geo2 = st.columns([7, 5])
    with c_geo1:
        state_df = GeographicalAnalyzer.analyze_by_region(filtered_df, region_col="state")
        if not state_df.empty:
            fig_geo_bar = create_bar_chart(
                df=state_df.head(10),
                x_col="total_accidents",
                y_col="state",
                title="Top 10 States/Regions by Crash Count",
                orientation="h"
            )
            st.plotly_chart(fig_geo_bar, use_container_width=True)
        else:
            st.info("No regional columns detected in current view.")

    with c_geo2:
        st.markdown("#### 🎯 Critical Regional Statistics")
        if not state_df.empty:
            st.dataframe(
                state_df[["rank", "state", "total_accidents", "fatalities", "fatality_rate_pct"]].head(10).rename(
                    columns={"rank": "#", "state": "Region", "total_accidents": "Crashes", "fatalities": "Deaths", "fatality_rate_pct": "Death Rate %"}
                ),
                hide_index=True,
                use_container_width=True
            )

with tab3:
    c_sev1, c_sev2 = st.columns([6, 6])
    with c_sev1:
        sev_df = SeverityAnalyzer.analyze_severity_distribution(filtered_df)
        if not sev_df.empty:
            fig_donut = create_donut_chart(
                df=sev_df,
                names_col="accident_severity",
                values_col="total_accidents",
                title="Accident Volume by Severity Classification"
            )
            st.plotly_chart(fig_donut, use_container_width=True)
        else:
            st.info("Severity categories not present.")

    with c_sev2:
        st.markdown("#### ⚡ Fatality Impact by Collision Severity")
        if not sev_df.empty:
            fig_fat_bar = create_bar_chart(
                df=sev_df,
                x_col="accident_severity",
                y_col="fatalities",
                title="Total Fatalities per Severity Level",
                color="#ef4444"
            )
            st.plotly_chart(fig_fat_bar, use_container_width=True)

