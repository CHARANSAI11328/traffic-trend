"""
Data and Metric Formatting Utilities
"""
from typing import Union, Optional
import math

def format_number(val: Union[int, float, None], precision: int = 0) -> str:
    """Formats numeric values into human-readable compact notation (e.g. 1,234 or 12.3K)."""
    if val is None or (isinstance(val, float) and math.isnan(val)):
        return "N/A"
    try:
        val = float(val)
        if abs(val) >= 1_000_000:
            return f"{val / 1_000_000:.2f}M"
        elif abs(val) >= 10_000:
            return f"{val / 1_000:.1f}k"
        elif precision == 0:
            return f"{int(round(val)):,}"
        else:
            return f"{val:,.{precision}f}"
    except (ValueError, TypeError):
        return "N/A"

def format_percentage(val: Union[int, float, None], show_sign: bool = True, precision: int = 1) -> str:
    """Formats float/decimal into percentage string with optional +/- prefix."""
    if val is None or (isinstance(val, float) and math.isnan(val)):
        return "N/A"
    try:
        val = float(val)
        prefix = "+" if show_sign and val > 0 else ""
        return f"{prefix}{val:.{precision}f}%"
    except (ValueError, TypeError):
        return "N/A"

def format_rate(numerator: Union[int, float], denominator: Union[int, float], multiplier: int = 100) -> str:
    """Computes and formats a safe rate."""
    if not denominator or denominator == 0 or math.isnan(denominator):
        return "0.0%"
    try:
        rate = (numerator / denominator) * multiplier
        return f"{rate:.1f}%"
    except (ZeroDivisionError, TypeError):
        return "0.0%"

def get_severity_badge_html(severity: str) -> str:
    """Generates an HTML badge for crash severity levels."""
    sev = str(severity).strip().lower()
    if "fatal" in sev:
        bg, border, text = "#450a0a", "#ef4444", "#fca5a5"
        label = "Fatal"
    elif "grievous" in sev or "serious" in sev:
        bg, border, text = "#431407", "#f97316", "#fdba74"
        label = "Grievous Injury"
    elif "minor" in sev or "slight" in sev:
        bg, border, text = "#422006", "#eab308", "#fde047"
        label = "Minor Injury"
    else:
        bg, border, text = "#064e3b", "#10b981", "#6ee7b7"
        label = "Property Damage Only"

    return f'<span style="background-color: {bg}; border: 1px solid {border}; color: {text}; font-size: 0.75rem; font-weight: 600; padding: 2px 8px; border-radius: 4px; text-transform: uppercase;">{label}</span>'

