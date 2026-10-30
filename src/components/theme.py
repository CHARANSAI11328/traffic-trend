"""
Theme & Custom Styling Engine for TRAFFIC TREND Platform
Injects deep navy/charcoal styling, polished cards, and typography.
"""
import streamlit as st

def inject_custom_theme() -> None:
    """Injects production-grade dark analytics UI CSS into Streamlit page."""
    custom_css = """
    <style>
    /* Global Background and Typography */
    .stApp {
        background-color: #0d1117;
        color: #f0f6fc;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }

    /* Main Container Padding */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        padding-left: 2.5rem;
        padding-right: 2.5rem;
        max-width: 1400px;
    }

    /* Top Header Branding Banner */
    .brand-banner {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 1.25rem 1.75rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
    }
    .brand-title {
        color: #38bdf8;
        font-size: 1.6rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .brand-subtitle {
        color: #94a3b8;
        font-size: 0.9rem;
        margin-top: 0.25rem;
        font-weight: 400;
    }

    /* Custom Metric Cards */
    .kpi-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 1.1rem 1.25rem;
        margin-bottom: 0.75rem;
        transition: transform 0.15s ease, border-color 0.15s ease;
    }
    .kpi-card:hover {
        border-color: #38bdf8;
        transform: translateY(-2px);
    }
    .kpi-label {
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #8b949e;
        margin-bottom: 0.35rem;
    }
    .kpi-value {
        font-size: 1.8rem;
        font-weight: 800;
        color: #f0f6fc;
        line-height: 1.1;
    }
    .kpi-delta {
        font-size: 0.8rem;
        font-weight: 600;
        margin-top: 0.35rem;
        display: flex;
        align-items: center;
        gap: 0.25rem;
    }
    .delta-pos {
        color: #ef4444; /* Increases in crashes are negative from safety perspective */
    }
    .delta-neg {
        color: #10b981; /* Decreases in crashes are positive */
    }
    .delta-neutral {
        color: #94a3b8;
    }

    /* Section Cards */
    .analytics-section {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 1.25rem 1.5rem;
        margin-top: 1rem;
        margin-bottom: 1.25rem;
    }
    .section-title {
        color: #e2e8f0;
        font-size: 1.1rem;
        font-weight: 700;
        margin-bottom: 0.75rem;
        border-bottom: 1px solid #21262d;
        padding-bottom: 0.5rem;
    }

    /* Status Badges */
    .badge-critical {
        background-color: #450a0a;
        color: #fca5a5;
        border: 1px solid #ef4444;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .badge-warning {
        background-color: #422006;
        color: #fde047;
        border: 1px solid #eab308;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .badge-success {
        background-color: #064e3b;
        color: #6ee7b7;
        border: 1px solid #10b981;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
    }
    .badge-info {
        background-color: #0c4a6e;
        color: #7dd3fc;
        border: 1px solid #0284c7;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 0.75rem;
        font-weight: 600;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #0b0f17;
        border-right: 1px solid #21262d;
    }
    section[data-testid="stSidebar"] .block-container {
        padding-top: 1.5rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
        border-bottom: 1px solid #30363d;
    }
    .stTabs [data-baseweb="tab"] {
        height: 42px;
        white-space: pre-wrap;
        background-color: #161b22;
        border-radius: 6px 6px 0px 0px;
        border: 1px solid #30363d;
        border-bottom: none;
        color: #8b949e;
        font-weight: 600;
        padding: 8px 16px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1f2937 !important;
        color: #38bdf8 !important;
        border-top: 2px solid #38bdf8 !important;
    }

    /* Dataframe table styling */
    [data-testid="stDataFrame"] {
        border: 1px solid #30363d;
        border-radius: 6px;
    }

    /* Buttons */
    .stButton>button {
        background-color: #1e293b;
        color: #f0f6fc;
        border: 1px solid #334155;
        border-radius: 6px;
        font-weight: 600;
        transition: all 0.15s ease;
    }
    .stButton>button:hover {
        background-color: #0284c7;
        border-color: #38bdf8;
        color: #ffffff;
    }
    .stButton>button[kind="primary"] {
        background-color: #0284c7;
        border-color: #38bdf8;
        color: #ffffff;
    }
    .stButton>button[kind="primary"]:hover {
        background-color: #0369a1;
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)

def render_brand_header(title: str, subtitle: str) -> None:
    """Renders the top banner for each analytics module."""
    html = f"""
    <div class="brand-banner">
        <h1 class="brand-title">🚦 {title}</h1>
        <div class="brand-subtitle">{subtitle}</div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

