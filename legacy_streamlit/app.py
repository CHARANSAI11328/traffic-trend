"""
TRAFFIC TREND — Road Accident Data Analysis & Intelligence Platform
Main Application Entrypoint
"""
import streamlit as st
import pandas as pd
from src.utils.configuration import CONFIG
from src.components.theme import inject_custom_theme, render_brand_header
from src.components.cards import render_kpi_card, render_filter_summary
from src.components.charts import (
    create_time_series_chart, create_bar_chart, create_donut_chart, create_geospatial_scatter_map
)
from src.analytics.kpis import KPICalculator
from src.analytics.trends import TrendAnalyzer
from src.analytics.geographical import GeographicalAnalyzer
from src.utils.state import get_current_data, render_sidebar_filters, initialize_app_state

# Page configuration
st.set_page_config(
    page_title=f"{CONFIG.APP_NAME} | Road Accident Intelligence",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply dark theme
inject_custom_theme()
initialize_app_state()

# Header Banner
render_brand_header(
    title=CONFIG.APP_NAME,
    subtitle="Institutional Road Safety Intelligence, Spatiotemporal Analysis & Casualty Risk Platform"
)

# Load data and apply filters
raw_df, enriched_df = get_current_data()

if enriched_df.empty:
    st.warning("⚠️ No dataset currently available. Please visit the **Data Management Center** to upload or load data.")
    st.stop()

filtered_df, active_filters = render_sidebar_filters(enriched_df)

# Render Filter Summary
render_filter_summary(len(filtered_df), len(enriched_df), active_filters)

# Compute Executive KPIs
kpis = KPICalculator.compute(filtered_df)

# KPI Cards Grid (4 columns)
col1, col2, col3, col4 = st.columns(4)
with col1:
    render_kpi_card(
        label="Total Recorded Crashes",
        value=f"{kpis.total_accidents:,}",
        delta=kpis.accidents_delta_pct,
        icon="💥"
    )
with col2:
    render_kpi_card(
        label="Total Fatalities",
        value=f"{kpis.total_fatalities:,}",
        delta=kpis.fatalities_delta_pct,
        icon="💀"
    )
with col3:
    render_kpi_card(
        label="Total Persons Injured",
        value=f"{kpis.total_injured:,}",
        delta=kpis.injured_delta_pct,
        icon="🩹"
    )
with col4:
    render_kpi_card(
        label="Fatality Rate",
        value=f"{kpis.fatality_rate_pct:.1f}%",
        delta_text=f"{kpis.casualty_rate_per_crash:.2f} casualties/crash",
        icon="⚠️"
    )

st.markdown("<br>", unsafe_allow_html=True)

# High-Level Visual Highlights
row1_col1, row1_col2 = st.columns([7, 5])

with row1_col1:
    st.markdown("#### 📈 Longitudinal Crash Trajectory")
    yearly_df = TrendAnalyzer.analyze_yearly_trend(filtered_df)
    if not yearly_df.empty:
        fig_trend = create_time_series_chart(
            df=yearly_df,
            x_col="year",
            y_cols=["total_accidents", "fatalities"],
            title="Annual Accidents & Fatality Counts (Multi-Year)",
            labels=["Total Accidents", "Recorded Fatalities"]
        )
        st.plotly_chart(fig_trend, use_container_width=True)
    else:
        st.info("Longitudinal data by year not present in current filtered subset.")

with row1_col2:
    st.markdown("#### 🚨 Crash Severity Distribution")
    if "accident_severity" in filtered_df.columns:
        sev_counts = filtered_df["accident_severity"].value_counts().reset_index()
        sev_counts.columns = ["Severity", "Count"]
        fig_sev = create_donut_chart(
            df=sev_counts,
            names_col="Severity",
            values_col="Count",
            title="Proportion of Crash Severity Classes"
        )
        st.plotly_chart(fig_sev, use_container_width=True)
    else:
        st.info("Severity category column not available.")

st.markdown("<br>", unsafe_allow_html=True)

# Row 2: Top Affected Regions & Hotspots Map Preview
row2_col1, row2_col2 = st.columns([6, 6])

with row2_col1:
    st.markdown("#### 🗺️ Regional Hotspot Concentration")
    geo_df = GeographicalAnalyzer.analyze_by_region(filtered_df, region_col="state")
    if not geo_df.empty:
        top_10_geo = geo_df.head(8)
        fig_geo = create_bar_chart(
            df=top_10_geo,
            x_col="total_accidents",
            y_col="state",
            title="Top Jurisdictions by Recorded Crashes",
            orientation="h"
        )
        st.plotly_chart(fig_geo, use_container_width=True)
    else:
        st.info("Regional state/province dimensions not found.")

with row2_col2:
    st.markdown("#### 📍 Spatial Coordinate Clusters")
    if "latitude" in filtered_df.columns and "longitude" in filtered_df.columns:
        fig_map = create_geospatial_scatter_map(
            df=filtered_df,
            title="Spatial Cluster Density (GPS Coordinates)"
        )
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.info("Geographic GPS coordinates (lat/lon) not present in active dataset.")

st.markdown("---")

# Quick Navigation Grid to Specialized Modules
st.markdown("### 🧭 Platform Intelligence Modules")
m_col1, m_col2, m_col3 = st.columns(3)

with m_col1:
    st.markdown("""
    <div class="kpi-card">
        <h4 style="color: #38bdf8; margin: 0 0 6px 0;">🔍 Accident Exploration</h4>
        <p style="color: #94a3b8; font-size: 0.85rem; margin-bottom: 8px;">Explore collision categories, contributing driver violations, road surfaces, and vehicle classes.</p>
        <span class="badge-info">Module B</span>
    </div>
    """, unsafe_allow_html=True)

with m_col2:
    st.markdown("""
    <div class="kpi-card">
        <h4 style="color: #38bdf8; margin: 0 0 6px 0;">🗺️ Geographical Intelligence</h4>
        <p style="color: #94a3b8; font-size: 0.85rem; margin-bottom: 8px;">State and district concentration rankings, urban vs rural morbidity, and high-density cluster maps.</p>
        <span class="badge-info">Module C</span>
    </div>
    """, unsafe_allow_html=True)

with m_col3:
    st.markdown("""
    <div class="kpi-card">
        <h4 style="color: #38bdf8; margin: 0 0 6px 0;">⏱️ Temporal & Diurnal Trends</h4>
        <p style="color: #94a3b8; font-size: 0.85rem; margin-bottom: 8px;">24-hour diurnal curves, rush-hour peak windows, day-of-week heatmaps, and rolling 7-day moving averages.</p>
        <span class="badge-info">Module D</span>
    </div>
    """, unsafe_allow_html=True)

m_col4, m_col5, m_col6 = st.columns(3)
with m_col4:
    st.markdown("""
    <div class="kpi-card">
        <h4 style="color: #38bdf8; margin: 0 0 6px 0;">🚑 Severity & Casualties</h4>
        <p style="color: #94a3b8; font-size: 0.85rem; margin-bottom: 8px;">Fatality ratios, vulnerable road users (two-wheelers, pedestrians), and weather-adjusted severity index.</p>
        <span class="badge-info">Module E</span>
    </div>
    """, unsafe_allow_html=True)

with m_col5:
    st.markdown("""
    <div class="kpi-card">
        <h4 style="color: #38bdf8; margin: 0 0 6px 0;">⚡ Risk Intelligence & Forecasts</h4>
        <p style="color: #94a3b8; font-size: 0.85rem; margin-bottom: 8px;">Composite Risk Priority Index (RPI), statistical Z-score volume surge detection, and baseline forecasting.</p>
        <span class="badge-info">Module F</span>
    </div>
    """, unsafe_allow_html=True)

with m_col6:
    st.markdown("""
    <div class="kpi-card">
        <h4 style="color: #38bdf8; margin: 0 0 6px 0;">💾 Data Management Center</h4>
        <p style="color: #94a3b8; font-size: 0.85rem; margin-bottom: 8px;">Upload CSV/Excel datasets, inspect schemas, apply configurable cleaning, view audit history, and export.</p>
        <span class="badge-success">Data Hub</span>
    </div>
    """, unsafe_allow_html=True)

