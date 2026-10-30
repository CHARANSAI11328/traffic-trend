"""
Module E — Severity & Casualty Deep-Dive Analysis
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
from src.analytics.kpis import KPICalculator
from src.utils.state import get_current_data, render_sidebar_filters

st.set_page_config(page_title="Severity Analysis | TRAFFIC TREND", page_icon="🚑", layout="wide")
inject_custom_theme()

render_brand_header(
    title="Module E: Severity Dynamics & Casualty Morbidity",
    subtitle="Rigorous Analysis of Fatalities, Severe Injuries, Vulnerable Road Users, and Lethality Ratios"
)

raw_df, enriched_df = get_current_data()
if enriched_df.empty:
    st.warning("No active dataset loaded.")
    st.stop()

filtered_df, active_filters = render_sidebar_filters(enriched_df)
render_filter_summary(len(filtered_df), len(enriched_df), active_filters)

# Dynamic KPIs for Severity
kpis = KPICalculator.compute(filtered_df)

c1, c2, c3, c4 = st.columns(4)
with c1:
    render_kpi_card("Fatal Incidents", f"{kpis.fatal_accidents_count:,}", icon="⚠️")
with c2:
    render_kpi_card("Non-Fatal Incidents", f"{kpis.non_fatal_accidents_count:,}", icon="🛡️")
with c3:
    render_kpi_card("Total Lives Lost", f"{kpis.total_fatalities:,}", icon="💀")
with c4:
    render_kpi_card("Persons Injured", f"{kpis.total_injured:,}", icon="🩹")

st.markdown("<br>", unsafe_allow_html=True)

# Tabs
sev_tab1, sev_tab2, sev_tab3 = st.tabs([
    "🚨 Severity Class Hierarchy",
    "🏍️ Modality & Vehicle Lethality",
    "🛣️ Road Environment Severity"
])

with sev_tab1:
    col1, col2 = st.columns([6, 6])
    sev_df = SeverityAnalyzer.analyze_severity_distribution(filtered_df)
    with col1:
        if not sev_df.empty:
            fig_sev = create_donut_chart(
                df=sev_df,
                names_col="accident_severity",
                values_col="total_accidents",
                title="Accidents by Severity Tier"
            )
            st.plotly_chart(fig_sev, use_container_width=True)
        else:
            st.info("Severity categories not present.")

    with col2:
        if not sev_df.empty:
            fig_morb = create_bar_chart(
                df=sev_df,
                x_col="accident_severity",
                y_col="fatalities",
                title="Fatalities Distributed by Severity Tier",
                color="#ef4444"
            )
            st.plotly_chart(fig_morb, use_container_width=True)

    if not sev_df.empty:
        st.markdown("#### 📋 Detailed Severity & Fatality Breakdown")
        st.dataframe(
            sev_df.rename(columns={
                "accident_severity": "Severity Classification",
                "total_accidents": "Incident Count",
                "fatalities": "Lives Lost",
                "injuries": "Persons Injured",
                "pct_of_total": "% of All Crashes",
                "fatality_rate_pct": "Fatality Rate (%)"
            }),
            hide_index=True,
            use_container_width=True
        )

with sev_tab2:
    v_col1, v_col2 = st.columns([7, 5])
    veh_df = SeverityAnalyzer.analyze_by_vehicle_type(filtered_df)
    with v_col1:
        if not veh_df.empty:
            fig_veh_fat = create_bar_chart(
                df=veh_df,
                x_col="fatality_rate_pct",
                y_col="primary_vehicle_type",
                title="Fatality Rate (%) by Primary Vehicle Involved",
                orientation="h",
                color="#f97316",
                hover_fmt=".1f"
            )
            st.plotly_chart(fig_veh_fat, use_container_width=True)
        else:
            st.info("Vehicle type column not found.")

    with v_col2:
        st.markdown("#### ⚠️ High-Fatality Vulnerable Road Users")
        st.caption("Pedestrians, cyclists, and two-wheelers face disproportionate lethality upon impact.")
        if not veh_df.empty:
            st.dataframe(
                veh_df[["primary_vehicle_type", "total_accidents", "fatalities", "fatality_rate_pct"]].rename(
                    columns={
                        "primary_vehicle_type": "Vehicle Modality",
                        "total_accidents": "Crash Count",
                        "fatalities": "Fatalities",
                        "fatality_rate_pct": "Lethality %"
                    }
                ),
                hide_index=True,
                use_container_width=True
            )

with sev_tab3:
    r_data = SeverityAnalyzer.analyze_by_road_and_weather(filtered_df)
    if "road_type" in r_data:
        st.markdown("#### 🛣️ Fatality Rate across Road Classifications")
        fig_r_fat = create_bar_chart(
            df=r_data["road_type"],
            x_col="road_type",
            y_col="fatality_rate_pct",
            title="Recorded Deaths per 100 Crashes by Road Type",
            color="#ef4444"
        )
        st.plotly_chart(fig_r_fat, use_container_width=True)
    else:
        st.info("Road classification column not found.")

