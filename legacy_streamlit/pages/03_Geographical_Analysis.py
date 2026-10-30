"""
Module C — Geographical Intelligence & Spatial Hotspots
TRAFFIC TREND — Road Accident Data Analysis & Intelligence Platform
"""
import streamlit as st
import pandas as pd
from src.components.theme import inject_custom_theme, render_brand_header
from src.components.cards import render_kpi_card, render_filter_summary
from src.components.charts import (
    create_bar_chart, create_geospatial_scatter_map, create_donut_chart
)
from src.analytics.geographical import GeographicalAnalyzer
from src.utils.state import get_current_data, render_sidebar_filters

st.set_page_config(page_title="Geographical Analysis | TRAFFIC TREND", page_icon="🗺️", layout="wide")
inject_custom_theme()

render_brand_header(
    title="Module C: Geographical Intelligence & Spatial Hotspots",
    subtitle="State & District Incident Densities, Urban vs Rural Divergence, and GPS Coordinate Clusters"
)

raw_df, enriched_df = get_current_data()
if enriched_df.empty:
    st.warning("No active dataset loaded.")
    st.stop()

filtered_df, active_filters = render_sidebar_filters(enriched_df)
render_filter_summary(len(filtered_df), len(enriched_df), active_filters)

# 1. Geospatial Map Section
st.markdown("### 📍 High-Resolution Coordinate Hotspots Map")
has_coords = "latitude" in filtered_df.columns and "longitude" in filtered_df.columns

if has_coords:
    coords_df = GeographicalAnalyzer.extract_hotspots_coordinates(filtered_df)
    if not coords_df.empty:
        fig_map = create_geospatial_scatter_map(
            df=coords_df,
            title=f"Georeferenced Crash Sites ({len(coords_df):,} Geo-located Points)"
        )
        st.plotly_chart(fig_map, use_container_width=True)
    else:
        st.info("No valid non-null coordinates within terrestrial boundaries in active filtered records.")
else:
    st.info("Geographic latitude/longitude coordinates are not present in this dataset. Falling back to regional aggregated views below.")

st.markdown("<br>", unsafe_allow_html=True)

# 2. State & District Breakdown Tabs
geo_tab1, geo_tab2, geo_tab3 = st.tabs(["🏛️ State / Province Ranking", "🏙️ District / City Analysis", "🏘️ Urban vs Rural Exposure"])

with geo_tab1:
    col1, col2 = st.columns([7, 5])
    state_df = GeographicalAnalyzer.analyze_by_region(filtered_df, region_col="state")
    with col1:
        if not state_df.empty:
            fig_state = create_bar_chart(
                df=state_df.head(15),
                x_col="total_accidents",
                y_col="state",
                title="Top States / Provinces by Crash Count",
                orientation="h"
            )
            st.plotly_chart(fig_state, use_container_width=True)
        else:
            st.info("State/Province dimension not found.")

    with col2:
        st.markdown("#### 📋 Complete State Ranking Table")
        if not state_df.empty:
            st.dataframe(
                state_df[["rank", "state", "total_accidents", "pct_of_total_accidents", "fatalities", "fatality_rate_pct"]].rename(
                    columns={
                        "rank": "Rank",
                        "state": "State / Jurisdiction",
                        "total_accidents": "Crashes",
                        "pct_of_total_accidents": "% Share",
                        "fatalities": "Deaths",
                        "fatality_rate_pct": "Fatality Rate %"
                    }
                ),
                hide_index=True,
                use_container_width=True
            )

with geo_tab2:
    d_col1, d_col2 = st.columns([7, 5])
    dist_df = GeographicalAnalyzer.analyze_by_region(filtered_df, region_col="district")
    with d_col1:
        if not dist_df.empty:
            fig_dist = create_bar_chart(
                df=dist_df.head(15),
                x_col="total_accidents",
                y_col="district",
                title="Top 15 Districts / Cities by Crash Count",
                orientation="h",
                color="#2dd4bf"
            )
            st.plotly_chart(fig_dist, use_container_width=True)
        else:
            st.info("District/City dimension not found in current dataset.")

    with d_col2:
        st.markdown("#### 📋 District Ranking Table")
        if not dist_df.empty:
            st.dataframe(
                dist_df[["rank", "district", "total_accidents", "fatalities", "fatality_rate_pct"]].head(20).rename(
                    columns={
                        "rank": "#",
                        "district": "District / City",
                        "total_accidents": "Crashes",
                        "fatalities": "Deaths",
                        "fatality_rate_pct": "Fatality Rate %"
                    }
                ),
                hide_index=True,
                use_container_width=True
            )

with geo_tab3:
    u_col1, u_col2 = st.columns([6, 6])
    urban_df = GeographicalAnalyzer.analyze_urban_vs_rural(filtered_df)
    with u_col1:
        if not urban_df.empty:
            fig_urban = create_donut_chart(
                df=urban_df,
                names_col=urban_df.columns[0],
                values_col="total_accidents",
                title="Accident Volume: Urban vs Rural"
            )
            st.plotly_chart(fig_urban, use_container_width=True)
        else:
            st.info("Urban / Rural locality category not recorded.")

    with u_col2:
        if not urban_df.empty:
            st.markdown("#### 🚨 Rural vs Urban Severity Disparity")
            st.dataframe(urban_df, hide_index=True, use_container_width=True)

