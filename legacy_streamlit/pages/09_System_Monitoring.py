"""
Module I — System Diagnostics, Telemetry & Health Monitoring
TRAFFIC TREND — Road Accident Data Analysis & Intelligence Platform
"""
import streamlit as st
import pandas as pd
from src.components.theme import inject_custom_theme, render_brand_header
from src.components.cards import render_kpi_card
from src.monitoring.health import SystemHealthMonitor
from src.monitoring.data_freshness import DataFreshnessAuditor
from src.database.repository import DatasetRepository
from src.utils.state import get_current_data

st.set_page_config(page_title="System Monitoring | TRAFFIC TREND", page_icon="📡", layout="wide")
inject_custom_theme()

render_brand_header(
    title="System Diagnostics & Telemetry Center",
    subtitle="Engine Health, Database Query Latency, Filesystem Write Latency, Data Freshness, and Execution Audit Trails"
)

raw_df, enriched_df = get_current_data()

# Collect diagnostics
health = SystemHealthMonitor.get_full_health_status()
freshness = DataFreshnessAuditor.evaluate_freshness(enriched_df)

# Top Status Indicators
c1, c2, c3, c4 = st.columns(4)
with c1:
    sys_stat = health["system_status"]
    render_kpi_card("Engine Status", sys_stat, icon="🟢" if sys_stat == "OPERATIONAL" else "🔴")
with c2:
    db_lat = health["database"]["latency_ms"]
    render_kpi_card("DB Latency", f"{db_lat:.1f} ms", icon="⚡")
with c3:
    fresh_tier = freshness["freshness_tier"]
    render_kpi_card("Data Freshness", fresh_tier, icon="📅")
with c4:
    app_ver = health["app_version"]
    render_kpi_card("Platform Version", f"v{app_ver}", icon="🏷️")

st.markdown("<br>", unsafe_allow_html=True)

# Data Freshness & Ingestion Status
st.markdown("### 📡 Data Feed & Ingestion Status")
st.markdown(f"""
<div style="background-color: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 1.25rem; margin-bottom: 1.5rem;">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
        <b style="color: #f0f6fc; font-size: 1.1rem;">Source Connection Status</b>
        <span class="badge-warning">Historical / Uploaded Dataset — Live Feed Not Connected</span>
    </div>
    <div style="color: #94a3b8; font-size: 0.9rem; line-height: 1.5;">
        • <b>Active Source Name:</b> <code>{freshness['dataset_name']}</code><br>
        • <b>Source Provenance:</b> <code>{freshness.get('source_type', 'Demonstration')}</code><br>
        • <b>Last Ingestion Timestamp:</b> <code>{freshness['last_import_time']}</code><br>
        • <b>Latest Incident Recorded:</b> <code>{freshness['latest_incident_date']}</code><br>
        • <b>Live Feed Connector:</b> <i>Offline / Not Configured. Platform strictly displays uploaded and audited historical datasets. No unverified scraping or unauthorized gateways are enabled.</i>
    </div>
</div>
""", unsafe_allow_html=True)

# Diagnostic Tables Tabs
tab_db, tab_logs, tab_env = st.tabs(["🗄️ Database & Storage Diagnostics", "📜 Application Event Logs", "⚙️ Runtime Environment"])

with tab_db:
    st.markdown("#### Database Engine Parameters")
    db_info = health["database"]
    st.json({
        "Engine Dialect": db_info.get("dialect", "sqlite"),
        "Target Database": db_info.get("url", "traffic_trend.db"),
        "Connection Status": "CONNECTED" if db_info.get("connected") else "DISCONNECTED",
        "Query Ping Latency": f"{db_info.get('latency_ms')} ms",
        "Filesystem Storage Writable": health["filesystem"]["writable"]
    })

with tab_logs:
    st.markdown("#### 📜 Recent Operational Logs")
    logs = DatasetRepository.get_recent_logs(limit=25)
    if logs:
        log_df = pd.DataFrame(logs)
        st.dataframe(log_df[["created_at", "operation", "status", "details"]].rename(
            columns={"created_at": "Timestamp", "operation": "Operation", "status": "Level", "details": "Message"}
        ), hide_index=True, use_container_width=True)
    else:
        st.info("No system log events recorded yet.")

with tab_env:
    st.markdown("#### Platform Runtime Parameters")
    import sys
    st.json({
        "Python Version": sys.version,
        "Streamlit Version": st.__version__,
        "Pandas Version": pd.__version__,
        "App Directory": str(health.get("timestamp"))
    })

