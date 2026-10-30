"""
Session State & Caching Manager for TRAFFIC TREND Platform
Ensures state consistency, high-performance data caching, and global filter persistence.
"""
from typing import Tuple, Dict, Any, Optional
import streamlit as st
import pandas as pd
from pathlib import Path
from src.database.connection import init_db
from src.database.repository import DatasetRepository
from src.data.loader import DataLoader
from src.data.cleaner import DataCleaner
from src.data.transformer import DataTransformer
from src.utils.configuration import CONFIG, PROCESSED_DATA_DIR
from src.monitoring.logger import logger

@st.cache_data(show_spinner=False)
def load_and_prepare_dataset(file_path_str: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Cached loader that reads file, cleans it, enriches features, and returns (raw_df, enriched_df).
    Cached via Streamlit to ensure sub-second page switches without reloading disk files.
    """
    path = Path(file_path_str)
    if not path.exists():
        raise FileNotFoundError(f"Dataset file not found at: {file_path_str}")

    raw_df, meta = DataLoader.load_file(path)
    # Apply detected column mappings
    mapped_df = DataLoader.apply_canonical_mapping(raw_df, meta["detected_mappings"])
    # Clean
    cleaned_df, summary = DataCleaner.clean(mapped_df)
    # Transform / Enrich
    enriched_df = DataTransformer.enrich_features(cleaned_df)
    
    # Cache processed parquet to disk for ultra-fast query capability
    try:
        parquet_path = PROCESSED_DATA_DIR / f"{path.stem}_processed.parquet"
        enriched_df.to_parquet(parquet_path, index=False)
    except Exception as e:
        logger.warning(f"Could not persist processed parquet: {e}")

    return raw_df, enriched_df


def initialize_app_state() -> None:
    """Initializes SQLite tables, session state, and loads default demonstration dataset if needed."""
    if "db_initialized" not in st.session_state:
        init_db()
        st.session_state.db_initialized = True

    if "active_dataset_id" not in st.session_state:
        # Check active dataset in repository
        active = DatasetRepository.get_active_dataset()
        if not active:
            # Auto-register benchmark demo dataset
            if CONFIG.BENCHMARK_DEMO_PATH.exists():
                raw_df, meta = DataLoader.load_file(CONFIG.BENCHMARK_DEMO_PATH)
                record = DatasetRepository.register_dataset(
                    name=CONFIG.BENCHMARK_DEMO_FILENAME,
                    file_type="CSV",
                    source_type="Demonstration Benchmark",
                    file_size_bytes=CONFIG.BENCHMARK_DEMO_PATH.stat().st_size,
                    raw_path=str(CONFIG.BENCHMARK_DEMO_PATH),
                    record_count=len(raw_df),
                    column_count=len(raw_df.columns),
                    checksum=meta["checksum_sha256"]
                )
                DatasetRepository.record_import_event(
                    dataset_id=record.id,
                    status="SUCCESS",
                    original_records=len(raw_df),
                    retained_records=len(raw_df),
                    summary_notes="Initial platform startup: Seeded benchmark demonstration dataset."
                )
                st.session_state.active_dataset_id = record.id
                st.session_state.active_file_path = str(CONFIG.BENCHMARK_DEMO_PATH)
                st.session_state.active_dataset_name = record.dataset_name
        else:
            st.session_state.active_dataset_id = active["id"]
            st.session_state.active_file_path = active["raw_file_path"]
            st.session_state.active_dataset_name = active["dataset_name"]

    # Filter State Initialization
    if "filter_state" not in st.session_state:
        st.session_state.filter_state = {
            "state": "All",
            "year": "All",
            "severity": "All",
            "road_type": "All",
            "vehicle_type": "All",
            "weather": "All"
        }


def get_current_data() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Retrieves (raw_df, enriched_df) for currently active dataset."""
    initialize_app_state()
    path_str = st.session_state.get("active_file_path")
    if not path_str or not Path(path_str).exists():
        if CONFIG.BENCHMARK_DEMO_PATH.exists():
            path_str = str(CONFIG.BENCHMARK_DEMO_PATH)
            st.session_state.active_file_path = path_str
        else:
            return pd.DataFrame(), pd.DataFrame()
            
    return load_and_prepare_dataset(path_str)


def render_sidebar_filters(df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Renders dynamic multi-attribute filter controls in the sidebar.
    Returns (filtered_dataframe, active_filters_dict).
    """
    st.sidebar.markdown("### 🔍 Global Safety Filters")

    if df.empty:
        st.sidebar.info("No active dataset to filter.")
        return df, {}

    filters = {}
    filtered = df.copy()

    # 1. State / Region Filter
    if "state" in df.columns:
        states = ["All"] + sorted([str(s) for s in df["state"].dropna().unique() if s != "Unknown"])
        sel_state = st.sidebar.selectbox("State / Province", states, index=0, key="sb_state")
        filters["State"] = sel_state
        if sel_state != "All":
            filtered = filtered[filtered["state"].astype(str) == sel_state]

    # 2. Year Filter
    if "year" in df.columns:
        years_list = sorted([int(y) for y in df["year"].dropna().unique() if not pd.isna(y)])
        years = ["All"] + [str(y) for y in years_list]
        sel_year = st.sidebar.selectbox("Year", years, index=0, key="sb_year")
        filters["Year"] = sel_year
        if sel_year != "All":
            filtered = filtered[filtered["year"].astype(str) == sel_year]

    # 3. Severity Filter
    sev_col = next((c for c in ["accident_severity", "severity"] if c in df.columns), None)
    if sev_col:
        sevs = ["All"] + sorted([str(s) for s in df[sev_col].dropna().unique()])
        sel_sev = st.sidebar.selectbox("Accident Severity", sevs, index=0, key="sb_sev")
        filters["Severity"] = sel_sev
        if sel_sev != "All":
            filtered = filtered[filtered[sev_col].astype(str) == sel_sev]

    # 4. Road Type Filter
    if "road_type" in df.columns:
        roads = ["All"] + sorted([str(r) for r in df["road_type"].dropna().unique() if r != "Unknown"])
        sel_road = st.sidebar.selectbox("Road Classification", roads, index=0, key="sb_road")
        filters["Road Type"] = sel_road
        if sel_road != "All":
            filtered = filtered[filtered["road_type"].astype(str) == sel_road]

    # 5. Primary Vehicle Type Filter
    veh_col = next((c for c in ["primary_vehicle_type", "vehicle_type"] if c in df.columns), None)
    if veh_col:
        vehs = ["All"] + sorted([str(v) for v in df[veh_col].dropna().unique() if v != "Unknown"])
        sel_veh = st.sidebar.selectbox("Vehicle Category", vehs, index=0, key="sb_veh")
        filters["Vehicle"] = sel_veh
        if sel_veh != "All":
            filtered = filtered[filtered[veh_col].astype(str) == sel_veh]

    # Quick Reset Filters Button
    if st.sidebar.button("↺ Reset All Filters", use_container_width=True):
        st.session_state.sb_state = "All"
        st.session_state.sb_year = "All"
        if sev_col:
            st.session_state.sb_sev = "All"
        if "road_type" in df.columns:
            st.session_state.sb_road = "All"
        if veh_col:
            st.session_state.sb_veh = "All"
        st.rerun()

    # Sidebar Data Provenance & Freshness Badge
    st.sidebar.markdown("---")
    st.sidebar.markdown("#### 📡 Data Source Info")
    active_name = st.session_state.get("active_dataset_name", "Demonstration Benchmark")
    st.sidebar.caption(f"**Active Source:** `{active_name}`")
    st.sidebar.caption(f"**Records Loaded:** `{len(df):,}`")
    st.sidebar.markdown('<span class="badge-info">Mode: Historical / Uploaded</span>', unsafe_allow_html=True)
    st.sidebar.caption("Live external feed not connected.")

    return filtered, filters

