"""
Reusable Metric Cards and UI Display Widgets for TRAFFIC TREND Platform
"""
from typing import Optional, Any
import streamlit as st
from src.utils.formatting import format_number, format_percentage

def render_kpi_card(
    label: str,
    value: Any,
    delta: Optional[float] = None,
    delta_text: Optional[str] = None,
    is_higher_bad: bool = True,
    icon: str = "📊"
) -> None:
    """Renders a custom styled dark analytics metric card."""
    delta_html = ""
    if delta is not None:
        sign = "+" if delta > 0 else ""
        if delta == 0:
            delta_class = "delta-neutral"
            delta_symbol = "•"
        elif is_higher_bad:
            delta_class = "delta-pos" if delta > 0 else "delta-neg"
            delta_symbol = "▲" if delta > 0 else "▼"
        else:
            delta_class = "delta-neg" if delta > 0 else "delta-pos"
            delta_symbol = "▲" if delta > 0 else "▼"

        text = delta_text or f"{sign}{delta:.1f}% vs prior period"
        delta_html = f'<div class="kpi-delta {delta_class}">{delta_symbol} {text}</div>'

    html = f"""
    <div class="kpi-card">
        <div class="kpi-label">{icon} {label}</div>
        <div class="kpi-value">{value}</div>
        {delta_html}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def render_filter_summary(filtered_count: int, total_count: int, active_filters: dict) -> None:
    """Displays active filter badges and selection scope."""
    pct = (filtered_count / total_count * 100) if total_count > 0 else 0
    filter_tags = []
    for k, v in active_filters.items():
        if v and v != "All":
            filter_tags.append(f'<span class="badge-info">{k}: {v}</span>')

    filters_html = " ".join(filter_tags) if filter_tags else '<span class="badge-success">Unfiltered / Full Dataset</span>'
    html = f"""
    <div style="background-color: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 0.6rem 1rem; margin-bottom: 1rem; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.5rem;">
        <div style="font-size: 0.85rem; color: #94a3b8;">
            Scope: <b style="color: #f0f6fc;">{filtered_count:,}</b> of <b style="color: #f0f6fc;">{total_count:,}</b> records ({pct:.1f}%)
        </div>
        <div style="display: flex; gap: 0.4rem; align-items: center; flex-wrap: wrap;">
            {filters_html}
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)

def render_dataset_status_pill(status_text: str, is_active: bool = True) -> None:
    """Renders data freshness and connection badge in sidebar or header."""
    cls_name = "badge-success" if is_active else "badge-warning"
    st.markdown(f'<span class="{cls_name}">● {status_text}</span>', unsafe_allow_html=True)

