"""
Standardized Dark Analytics Plotly Visualization Engine for TRAFFIC TREND Platform
Consistent styling, custom colorways, clean legends, and interactive tooltips.
"""
from typing import List, Optional, Union
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from src.utils.configuration import Palette

CHART_THEME = {
    "layout": {
        "paper_bgcolor": "#161b22",
        "plot_bgcolor": "#161b22",
        "font": {"family": "-apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica", "color": "#f0f6fc", "size": 12},
        "margin": {"l": 40, "r": 30, "t": 50, "b": 40},
        "hovermode": "x unified",
        "xaxis": {
            "gridcolor": "#21262d",
            "linecolor": "#30363d",
            "zerolinecolor": "#30363d",
            "tickfont": {"color": "#8b949e", "size": 11}
        },
        "yaxis": {
            "gridcolor": "#21262d",
            "linecolor": "#30363d",
            "zerolinecolor": "#30363d",
            "tickfont": {"color": "#8b949e", "size": 11}
        },
        "legend": {
            "bgcolor": "rgba(22, 27, 34, 0.8)",
            "bordercolor": "#30363d",
            "borderwidth": 1,
            "font": {"color": "#f0f6fc"}
        }
    }
}

def apply_base_layout(fig: go.Figure, title: str, x_title: str = "", y_title: str = "") -> go.Figure:
    """Applies common dark theme styling to Plotly figure."""
    fig.update_layout(
        title={
            "text": f"<b>{title}</b>",
            "font": {"size": 14, "color": "#f0f6fc"},
            "x": 0.02,
            "xanchor": "left"
        },
        paper_bgcolor=CHART_THEME["layout"]["paper_bgcolor"],
        plot_bgcolor=CHART_THEME["layout"]["plot_bgcolor"],
        font=CHART_THEME["layout"]["font"],
        margin=CHART_THEME["layout"]["margin"],
        xaxis_title=x_title,
        yaxis_title=y_title,
        legend=CHART_THEME["layout"]["legend"]
    )
    fig.update_xaxes(gridcolor="#21262d", linecolor="#30363d", zerolinecolor="#30363d")
    fig.update_yaxes(gridcolor="#21262d", linecolor="#30363d", zerolinecolor="#30363d")
    return fig

def create_time_series_chart(
    df: pd.DataFrame,
    x_col: str,
    y_cols: List[str],
    title: str,
    labels: Optional[List[str]] = None,
    colors_list: Optional[List[str]] = None
) -> go.Figure:
    """Generates multi-line interactive time-series chart with area shading."""
    fig = go.Figure()
    palette = colors_list or Palette.CHART_COLORS

    for idx, y_c in enumerate(y_cols):
        color = palette[idx % len(palette)]
        name = (labels[idx] if labels and idx < len(labels) else y_c).replace("_", " ").title()
        
        fig.add_trace(go.Scatter(
            x=df[x_col],
            y=df[y_c],
            mode="lines+markers",
            name=name,
            line={"color": color, "width": 2.5},
            marker={"size": 6, "color": color},
            hovertemplate=f"<b>{name}</b>: %{{y:,}}<extra></extra>"
        ))

    apply_base_layout(fig, title=title, x_title=x_col.replace("_", " ").title())
    fig.update_layout(hovermode="x unified")
    return fig

def create_bar_chart(
    df: pd.DataFrame,
    x_col: str,
    y_col: str,
    title: str,
    orientation: str = "v",
    color: str = Palette.ACCENT_CYAN,
    hover_fmt: str = ",.0f"
) -> go.Figure:
    """Generates bar chart with customizable orientation and hover format."""
    fig = go.Figure()
    
    if orientation == "v":
        fig.add_trace(go.Bar(
            x=df[x_col],
            y=df[y_col],
            marker={"color": color, "line": {"color": "#38bdf8", "width": 1}},
            hovertemplate=f"<b>%{{x}}</b>: %{{y:{hover_fmt}}}<extra></extra>"
        ))
        apply_base_layout(fig, title=title, x_title=x_col.replace("_", " ").title(), y_title=y_col.replace("_", " ").title())
    else:
        fig.add_trace(go.Bar(
            x=df[y_col],
            y=df[x_col],
            orientation="h",
            marker={"color": color, "line": {"color": "#38bdf8", "width": 1}},
            hovertemplate=f"<b>%{{y}}</b>: %{{x:{hover_fmt}}}<extra></extra>"
        ))
        apply_base_layout(fig, title=title, x_title=y_col.replace("_", " ").title(), y_title=x_col.replace("_", " ").title())
        fig.update_yaxes(autorange="reversed")

    return fig

def create_donut_chart(
    df: pd.DataFrame,
    names_col: str,
    values_col: str,
    title: str,
    hole: float = 0.55
) -> go.Figure:
    """Generates modern donut chart with clear percentage callouts."""
    fig = go.Figure()
    
    fig.add_trace(go.Pie(
        labels=df[names_col],
        values=df[values_col],
        hole=hole,
        marker={"colors": Palette.CHART_COLORS, "line": {"color": "#161b22", "width": 2}},
        textinfo="percent+label",
        hoverinfo="label+value+percent",
        textfont={"color": "#f0f6fc", "size": 11}
    ))
    
    apply_base_layout(fig, title=title)
    fig.update_layout(showlegend=True)
    return fig

def create_geospatial_scatter_map(
    df: pd.DataFrame,
    lat_col: str = "latitude",
    lon_col: str = "longitude",
    severity_col: str = "accident_severity",
    fatalities_col: str = "fatalities_count",
    title: str = "Geographical Accident Hotspot Distribution"
) -> go.Figure:
    """Renders geographic coordinates using Plotly dark OpenStreetMap tiles."""
    fig = go.Figure()

    if df.empty or lat_col not in df.columns or lon_col not in df.columns:
        apply_base_layout(fig, title=f"{title} (No Coordinate Data Available)")
        return fig

    # Map colors by severity
    color_map = {
        "Fatal": Palette.FATAL_RED,
        "Grievous Injury": Palette.GRIEVOUS_ORANGE,
        "Minor Injury": Palette.MINOR_YELLOW,
        "Property Damage Only": Palette.SAFE_GREEN
    }

    temp = df.dropna(subset=[lat_col, lon_col]).copy()
    
    for sev_name, group in temp.groupby(severity_col if severity_col in temp.columns else fatalities_col):
        sev_str = str(sev_name)
        color = color_map.get(sev_str, Palette.ACCENT_CYAN)
        
        fig.add_trace(go.Scattermapbox(
            lat=group[lat_col],
            lon=group[lon_col],
            mode="markers",
            marker=go.scattermapbox.Marker(
                size=8,
                color=color,
                opacity=0.8
            ),
            name=sev_str,
            text=group.apply(
                lambda r: f"Location: {r.get('district', '')}, {r.get('state', '')}<br>"
                          f"Severity: {sev_str}<br>"
                          f"Fatalities: {r.get('fatalities_count', 0)} | Injured: {r.get('injured_count', 0)}",
                axis=1
            ),
            hoverinfo="text"
        ))

    # Center map on centroid
    center_lat = float(temp[lat_col].median()) if not temp.empty else 20.5937
    center_lon = float(temp[lon_col].median()) if not temp.empty else 78.9629

    fig.update_layout(
        title={"text": f"<b>{title}</b>", "font": {"size": 14, "color": "#f0f6fc"}},
        mapbox_style="carto-darkmatter",
        mapbox=dict(
            center=dict(lat=center_lat, lon=center_lon),
            zoom=4.5
        ),
        paper_bgcolor="#161b22",
        margin={"l": 0, "r": 0, "t": 40, "b": 0},
        legend={"bgcolor": "rgba(22, 27, 34, 0.8)", "font": {"color": "#f0f6fc"}}
    )
    return fig

def create_correlation_heatmap(corr_df: pd.DataFrame, title: str = "Feature Correlation Matrix") -> go.Figure:
    """Renders correlation matrix with diverging color scale."""
    fig = go.Figure()
    
    if corr_df.empty:
        apply_base_layout(fig, title=f"{title} (Insufficient Numeric Columns)")
        return fig

    z_vals = corr_df.values
    x_labels = [c.replace("_", " ").title() for c in corr_df.columns]
    y_labels = [r.replace("_", " ").title() for r in corr_df.index]

    fig.add_trace(go.Heatmap(
        z=z_vals,
        x=x_labels,
        y=y_labels,
        colorscale="RdBu_r",
        zmin=-1.0,
        zmax=1.0,
        text=np.around(z_vals, decimals=2),
        texttemplate="%{text}",
        textfont={"size": 11, "color": "#f0f6fc"}
    ))

    apply_base_layout(fig, title=title)
    return fig

def create_forecast_plot(forecast: Any, title: str = "Longitudinal Projection & Confidence Interval") -> go.Figure:
    """Renders historic series alongside forecasted trajectory and 95% confidence bounds."""
    fig = go.Figure()

    # Historical
    fig.add_trace(go.Scatter(
        x=forecast.historical_dates,
        y=forecast.historical_values,
        mode="lines+markers",
        name="Historical Observed",
        line={"color": Palette.ACCENT_CYAN, "width": 2.5},
        marker={"size": 5}
    ))

    # Upper bound
    fig.add_trace(go.Scatter(
        x=forecast.forecast_dates,
        y=forecast.upper_bound_95,
        mode="lines",
        line={"width": 0},
        showlegend=False,
        hoverinfo="skip"
    ))

    # Lower bound with fill
    fig.add_trace(go.Scatter(
        x=forecast.forecast_dates,
        y=forecast.lower_bound_95,
        mode="lines",
        line={"width": 0},
        fill="tonexty",
        fillcolor="rgba(99, 102, 241, 0.2)",
        name="95% Confidence Band",
        hoverinfo="skip"
    ))

    # Forecast projected line
    fig.add_trace(go.Scatter(
        x=forecast.forecast_dates,
        y=forecast.forecast_values,
        mode="lines+markers",
        name="Projected Baseline",
        line={"color": Palette.ACCENT_INDIGO, "width": 2.5, "dash": "dash"},
        marker={"size": 6, "symbol": "diamond"}
    ))

    apply_base_layout(fig, title=title, x_title="Timeline", y_title="Accident Volume")
    return fig

