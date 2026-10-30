"""
Module G — Data Management Center & Ingestion Pipeline
TRAFFIC TREND — Road Accident Data Analysis & Intelligence Platform
"""
import streamlit as st
import pandas as pd
from pathlib import Path
from src.components.theme import inject_custom_theme, render_brand_header
from src.components.cards import render_kpi_card
from src.data.loader import DataLoader
from src.data.cleaner import DataCleaner, CleaningOptions
from src.data.validator import DataValidator
from src.data.profiler import DataProfiler
from src.database.repository import DatasetRepository
from src.utils.configuration import CONFIG, RAW_DATA_DIR, PROCESSED_DATA_DIR
from src.utils.state import initialize_app_state, load_and_prepare_dataset
from src.monitoring.logger import logger

st.set_page_config(page_title="Data Management | TRAFFIC TREND", page_icon="💾", layout="wide")
inject_custom_theme()
initialize_app_state()

render_brand_header(
    title="Data Management Center",
    subtitle="Ingestion Pipeline, Schema Inspection, Configurable Data Cleansing, Quality Audits & Registry"
)

# Tabs
tab_upload, tab_clean, tab_registry, tab_history = st.tabs([
    "📥 Ingest New Dataset (CSV / Excel)",
    "🧹 Configurable Data Cleansing & Quality",
    "🗃️ Active Dataset Registry",
    "📜 Ingestion & Processing Audit Log"
])

# -------------------------------------------------------------------
# TAB 1: UPLOAD & INGESTION
# -------------------------------------------------------------------
with tab_upload:
    st.markdown("### 📥 Upload Road Accident Dataset")
    st.caption("Supports CSV, Excel (.xlsx, .xls), and Parquet files up to 200MB. Schema is automatically profiled and mapped.")

    uploaded_file = st.file_uploader(
        "Choose file:",
        type=["csv", "xlsx", "xls", "parquet"],
        help="Upload standard road accident records. Original files are preserved in pristine state."
    )

    if uploaded_file:
        try:
            with st.spinner("Profiling uploaded file structure..."):
                raw_df, meta = DataLoader.load_file(uploaded_file)
                
            st.success(f"✅ Successfully read **{meta['dataset_name']}**: {meta['record_count']:,} records across {meta['column_count']} columns.")

            # Summary metrics
            u1, u2, u3, u4 = st.columns(4)
            with u1:
                render_kpi_card("Total Records", f"{meta['record_count']:,}", icon="📋")
            with u2:
                render_kpi_card("Total Columns", meta['column_count'], icon="📊")
            with u3:
                render_kpi_card("File Size", f"{meta['file_size_bytes'] / 1024:.1f} KB", icon="💾")
            with u4:
                mapped_count = len(meta['detected_mappings'])
                render_kpi_card("Mapped Dimensions", f"{mapped_count} of 22", icon="🎯")

            # Column Mappings Table
            st.markdown("#### 🔍 Automated Column Schema Discovery")
            if meta['detected_mappings']:
                mapping_rows = [{"Canonical Dimension": k, "Detected Uploaded Column": v} for k, v in meta['detected_mappings'].items()]
                st.dataframe(pd.DataFrame(mapping_rows), hide_index=True, use_container_width=True)
            else:
                st.warning("No standard canonical columns were automatically detected. Generic names will be used.")

            # Dataset Preview
            st.markdown("#### 👁️ Raw Dataset Preview (First 10 Rows)")
            st.dataframe(raw_df.head(10), use_container_width=True)

            # Ingest to Database Action
            if st.button("🚀 Register & Activate This Dataset", type="primary", use_container_width=True):
                # Save raw file
                save_path = RAW_DATA_DIR / meta["dataset_name"]
                if hasattr(uploaded_file, "seek"):
                    uploaded_file.seek(0)
                with open(save_path, "wb") as f:
                    f.write(uploaded_file.read())

                # Register in database
                record = DatasetRepository.register_dataset(
                    name=meta["dataset_name"],
                    file_type=meta["file_type"],
                    source_type="Uploaded",
                    file_size_bytes=meta["file_size_bytes"],
                    raw_path=str(save_path),
                    record_count=meta["record_count"],
                    column_count=meta["column_count"],
                    checksum=meta["checksum_sha256"]
                )
                
                # Switch active dataset
                DatasetRepository.set_active_dataset(record.id)
                st.session_state.active_dataset_id = record.id
                st.session_state.active_file_path = str(save_path)
                st.session_state.active_dataset_name = record.dataset_name

                # Log event
                DatasetRepository.record_import_event(
                    dataset_id=record.id,
                    status="SUCCESS",
                    original_records=meta["record_count"],
                    retained_records=meta["record_count"],
                    summary_notes=f"User uploaded dataset '{meta['dataset_name']}'."
                )

                # Clear cache so new dataset loads immediately
                st.cache_data.clear()
                st.success(f"🎉 Dataset '{meta['dataset_name']}' is now the ACTIVE source across all platform analytics modules!")
                st.rerun()

        except Exception as e:
            st.error(f"Failed to process uploaded dataset: {e}")
            logger.error(f"Upload error: {e}", exc_info=True)

# -------------------------------------------------------------------
# TAB 2: DATA CLEANING & QUALITY SCORECARD
# -------------------------------------------------------------------
with tab_clean:
    st.markdown("### 🧹 Configurable Data Cleansing & Institutional Scorecard")
    
    active_dataset = DatasetRepository.get_active_dataset()
    if not active_dataset:
        st.info("Please register or activate a dataset first.")
    else:
        st.markdown(f"**Target Active Dataset:** `{active_dataset['dataset_name']}` ({active_dataset['record_count']:,} records)")
        
        # Load raw data for this active dataset
        raw_target_df, meta_target = DataLoader.load_file(active_dataset["raw_file_path"])
        mapped_target = DataLoader.apply_canonical_mapping(raw_target_df, meta_target["detected_mappings"])

        # Quality Scorecard BEFORE Cleaning
        st.markdown("#### 🏆 Data Quality Scorecard (Current State)")
        scorecard = DataProfiler.profile(mapped_target)
        
        q1, q2, q3, q4, q5 = st.columns(5)
        with q1:
            render_kpi_card("Overall Score", f"{scorecard.overall_score}/100", icon="🏅")
        with q2:
            render_kpi_card("Completeness (30%)", f"{scorecard.completeness_score}%", icon="📊")
        with q3:
            render_kpi_card("Uniqueness (25%)", f"{scorecard.uniqueness_score}%", icon="✨")
        with q4:
            render_kpi_card("Validity (25%)", f"{scorecard.validity_score}%", icon="✔️")
        with q5:
            render_kpi_card("Consistency (20%)", f"{scorecard.consistency_score}%", icon="⚖️")

        st.caption(f"**Calculated Grade:** `{scorecard.quality_grade}` | Missing Cells: `{scorecard.missing_cells_pct}%` | Duplicates: `{scorecard.duplicate_pct}%`")

        # Configurable Cleaning Options
        st.markdown("---")
        st.markdown("#### ⚙️ Configurable Cleaning Options")
        
        c_opt1, c_opt2 = st.columns(2)
        with c_opt1:
            drop_dups = st.checkbox("Remove Exact Duplicate Records", value=True)
            handle_dates = st.selectbox("Missing / Unparseable Dates Strategy:", ["drop", "coerce"], index=0)
            handle_cas = st.selectbox("Missing Casualty Numbers Strategy:", ["impute_zero", "drop"], index=0)

        with c_opt2:
            clamp_neg = st.checkbox("Enforce Non-Negative Casualties (Clamp < 0 to 0)", value=True)
            sanitize_coords = st.checkbox("Sanitize GPS Coordinates (Null values outside [-90, +90], [-180, +180])", value=True)
            impute_cat = st.checkbox("Impute Blank Categoricals with 'Unknown'", value=True)

        if st.button("🔍 Preview Cleaning Results", use_container_width=True):
            clean_opts = CleaningOptions(
                drop_duplicates=drop_dups,
                handle_missing_dates=handle_dates,
                handle_missing_casualties=handle_cas,
                enforce_non_negative_casualties=clamp_neg,
                validate_coordinates=sanitize_coords,
                impute_missing_categoricals=impute_cat
            )
            preview_cleaned, summary = DataCleaner.clean(mapped_target, clean_opts)
            
            st.markdown("##### 📋 Cleaning Execution Audit")
            st.write(f"- Original record count: **{summary.original_records:,}**")
            st.write(f"- Retained records: **{summary.retained_records:,}**")
            st.write(f"- Duplicates purged: **{summary.duplicates_removed:,}**")
            st.write(f"- Invalid date records dropped: **{summary.invalid_dates_dropped:,}**")
            st.write(f"- Missing casualty entries imputed: **{summary.missing_imputed_count:,}**")
            st.write(f"- Negative casualties clamped: **{summary.negative_casualties_corrected:,}**")
            st.write(f"- Out-of-bounds GPS coordinates nulled: **{summary.invalid_coordinates_nulled:,}**")
            
            st.markdown("##### 📝 Modifications Log:")
            for m in summary.modifications_log:
                st.caption(f"• {m}")

            # Option to save cleaned version
            if st.button("💾 Apply & Save Cleaned Dataset", type="primary"):
                processed_path = PROCESSED_DATA_DIR / f"{Path(active_dataset['dataset_name']).stem}_cleaned.parquet"
                preview_cleaned.to_parquet(processed_path, index=False)
                
                # Persist quality metrics to database
                new_scorecard = DataProfiler.profile(preview_cleaned)
                DatasetRepository.save_quality_metrics(
                    dataset_id=active_dataset["id"],
                    completeness=new_scorecard.completeness_score,
                    uniqueness=new_scorecard.uniqueness_score,
                    validity=new_scorecard.validity_score,
                    consistency=new_scorecard.consistency_score,
                    overall=new_scorecard.overall_score,
                    duplicate_pct=new_scorecard.duplicate_pct,
                    missing_pct=new_scorecard.missing_cells_pct,
                    invalid_date_count=new_scorecard.invalid_dates_count
                )
                
                # Record import event
                DatasetRepository.record_import_event(
                    dataset_id=active_dataset["id"],
                    status="SUCCESS",
                    original_records=summary.original_records,
                    retained_records=summary.retained_records,
                    duplicate_count=summary.duplicates_removed,
                    missing_values_handled=summary.missing_imputed_count,
                    invalid_records_dropped=summary.invalid_dates_dropped,
                    summary_notes=f"Cleaned dataset saved: {len(preview_cleaned)} records retained."
                )

                st.cache_data.clear()
                st.success(f"Cleaned dataset successfully committed to {processed_path}!")
                st.rerun()

# -------------------------------------------------------------------
# TAB 3: DATASET REGISTRY
# -------------------------------------------------------------------
with tab_registry:
    st.markdown("### 🗃️ Registered Datasets")
    datasets = DatasetRepository.get_all_datasets()
    
    if not datasets:
        st.info("No datasets registered.")
    else:
        for d in datasets:
            is_cur = d["is_active"]
            badge = '<span class="badge-success">ACTIVE</span>' if is_cur else '<span class="badge-info">INACTIVE</span>'
            st.markdown(f"""
            <div style="background-color: #161b22; border: 1px solid {'#38bdf8' if is_cur else '#30363d'}; border-radius: 6px; padding: 1rem; margin-bottom: 0.75rem;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <b style="color: #f0f6fc; font-size: 1.05rem;">{d['dataset_name']}</b>
                    <div>{badge}</div>
                </div>
                <div style="color: #94a3b8; font-size: 0.85rem; margin-top: 6px;">
                    Records: <b>{d['record_count']:,}</b> | Type: <b>{d['file_type']}</b> | Source: <b>{d['source_type']}</b> | Size: <b>{d['file_size_bytes']/1024:.1f} KB</b> | SHA256: <code>{str(d['checksum_sha256'])[:16]}...</code>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if not is_cur:
                if st.button(f"Switch to '{d['dataset_name']}'", key=f"btn_activate_{d['id']}"):
                    DatasetRepository.set_active_dataset(d["id"])
                    st.session_state.active_dataset_id = d["id"]
                    st.session_state.active_file_path = d["raw_file_path"]
                    st.session_state.active_dataset_name = d["dataset_name"]
                    st.cache_data.clear()
                    st.success(f"Switched active dataset to {d['dataset_name']}!")
                    st.rerun()

# -------------------------------------------------------------------
# TAB 4: IMPORT & AUDIT HISTORY
# -------------------------------------------------------------------
with tab_history:
    st.markdown("### 📜 Ingestion & Processing Audit Log")
    history = DatasetRepository.get_import_history(limit=25)
    if not history:
        st.info("No import events logged.")
    else:
        hist_df = pd.DataFrame(history)
        hist_display = hist_df[["timestamp", "dataset_id", "status", "original_records", "retained_records", "duplicate_count", "summary_notes"]].rename(
            columns={
                "timestamp": "Timestamp (UTC)",
                "dataset_id": "Dataset ID",
                "status": "Status",
                "original_records": "Raw Records",
                "retained_records": "Retained",
                "duplicate_count": "Duplicates",
                "summary_notes": "Audit Notes"
            }
        )
        st.dataframe(hist_display, hide_index=True, use_container_width=True)

