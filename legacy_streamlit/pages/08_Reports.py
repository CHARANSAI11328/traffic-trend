"""
Module H — Executive Reports & Data Extracts Center
TRAFFIC TREND — Road Accident Data Analysis & Intelligence Platform
"""
import streamlit as st
import pandas as pd
from pathlib import Path
from src.components.theme import inject_custom_theme, render_brand_header
from src.components.cards import render_kpi_card, render_filter_summary
from src.analytics.kpis import KPICalculator
from src.reports.pdf_generator import PDFReportGenerator
from src.reports.excel_exporter import ExcelExporter
from src.utils.state import get_current_data, render_sidebar_filters
from src.monitoring.logger import logger

st.set_page_config(page_title="Executive Reports | TRAFFIC TREND", page_icon="📑", layout="wide")
inject_custom_theme()

render_brand_header(
    title="Executive Reports & Export Intelligence Center",
    subtitle="Generate Institutional PDF Intelligence Briefs, Multi-Tab Excel Summaries, and Filtered Data Extracts"
)

raw_df, enriched_df = get_current_data()
if enriched_df.empty:
    st.warning("No active dataset loaded.")
    st.stop()

filtered_df, active_filters = render_sidebar_filters(enriched_df)
render_filter_summary(len(filtered_df), len(enriched_df), active_filters)

kpis = KPICalculator.compute(filtered_df)
active_name = st.session_state.get("active_dataset_name", "Current Dataset")

rep_col1, rep_col2 = st.columns(2)

# ----------------------------------------------------
# PDF GENERATION
# ----------------------------------------------------
with rep_col1:
    st.markdown("""
    <div class="kpi-card">
        <h3 style="color: #38bdf8; margin: 0 0 8px 0;">📄 Executive PDF Intelligence Brief</h3>
        <p style="color: #94a3b8; font-size: 0.9rem;">
            Generate a standardized, publication-grade PDF report containing executive KPIs, 
            severity tables, regional hotspot rankings, filter provenance, and analytical limitations.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("🖨️ Compile & Download PDF Report", type="primary", use_container_width=True):
        with st.spinner("Compiling ReportLab vector layout..."):
            try:
                filter_str = ", ".join([f"{k}: {v}" for k, v in active_filters.items() if v != "All"]) or "Full unfiltered dataset"
                pdf_path = PDFReportGenerator.generate_executive_report(
                    kpis=kpis,
                    df_filtered=filtered_df,
                    dataset_name=active_name,
                    filter_summary=filter_str
                )
                with open(pdf_path, "rb") as f:
                    pdf_bytes = f.read()

                st.download_button(
                    label="⬇️ Save Executive PDF to Computer",
                    data=pdf_bytes,
                    file_name=pdf_path.name,
                    mime="application/pdf",
                    use_container_width=True
                )
                st.success("✅ Executive PDF generated successfully!")
            except Exception as e:
                st.error(f"Failed to compile PDF: {e}")
                logger.error(f"PDF error: {e}", exc_info=True)

# ----------------------------------------------------
# EXCEL WORKBOOK GENERATION
# ----------------------------------------------------
with rep_col2:
    st.markdown("""
    <div class="kpi-card">
        <h3 style="color: #38bdf8; margin: 0 0 8px 0;">📊 Multi-Tab Excel Intelligence Workbook</h3>
        <p style="color: #94a3b8; font-size: 0.9rem;">
            Exports a formatted 5-worksheet OpenPyXL workbook featuring Executive KPI Summaries, 
            Regional Breakdowns, Severity matrices, Temporal aggregates, and Raw filtered records.
        </p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("📗 Build & Download Excel Workbook", type="primary", use_container_width=True):
        with st.spinner("Generating styled OpenPyXL spreadsheet..."):
            try:
                excel_path = ExcelExporter.export_workbook(
                    kpis=kpis,
                    df_filtered=filtered_df,
                    dataset_name=active_name
                )
                with open(excel_path, "rb") as f:
                    excel_bytes = f.read()

                st.download_button(
                    label="⬇️ Save Excel Workbook (.xlsx)",
                    data=excel_bytes,
                    file_name=excel_path.name,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
                st.success("✅ Multi-Tab Excel Workbook generated successfully!")
            except Exception as e:
                st.error(f"Failed to generate Excel workbook: {e}")
                logger.error(f"Excel error: {e}", exc_info=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("### 💾 Raw & Filtered Data Extract Downloads")

c_csv, c_prq = st.columns(2)

with c_csv:
    csv_data = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label=f"⬇️ Download Filtered CSV ({len(filtered_df):,} rows)",
        data=csv_data,
        file_name=f"Traffic_Trend_Filtered_Extract_{len(filtered_df)}rows.csv",
        mime="text/csv",
        use_container_width=True
    )

with c_prq:
    import io
    prq_buffer = io.BytesIO()
    filtered_df.to_parquet(prq_buffer, index=False)
    st.download_button(
        label=f"⬇️ Download Filtered Apache Parquet ({len(filtered_df):,} rows)",
        data=prq_buffer.getvalue(),
        file_name=f"Traffic_Trend_Filtered_Extract.parquet",
        mime="application/octet-stream",
        use_container_width=True
    )

