from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, Optional
import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from backend.app.core.config import settings

class ExcelExporter:
    """Exports multi-tab, formatted Excel workbooks."""

    @classmethod
    def export_analytics_workbook(
        cls,
        df_filtered: pd.DataFrame,
        kpis: Any,
        dataset_name: str,
        output_path: Optional[Path] = None
    ) -> Path:
        if output_path is None:
            ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            output_path = settings.EXPORTS_DATA_DIR / f"Traffic_Trend_Analytics_{ts}.xlsx"

        output_path.parent.mkdir(parents=True, exist_ok=True)
        wb = openpyxl.Workbook()

        # Styles
        header_fill = PatternFill(start_color="0F172A", end_color="0F172A", fill_type="solid")
        sub_fill = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
        header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
        title_font = Font(name="Calibri", size=16, bold=True, color="0F172A")
        sub_font = Font(name="Calibri", size=10, italic=True, color="475569")
        thin_border = Border(
            left=Side(style='thin', color='CBD5E1'),
            right=Side(style='thin', color='CBD5E1'),
            top=Side(style='thin', color='CBD5E1'),
            bottom=Side(style='thin', color='CBD5E1')
        )

        # Tab 1: Executive Summary
        ws_exec = wb.active
        ws_exec.title = "Executive Summary"
        ws_exec.views.sheetView[0].showGridLines = True

        ws_exec.append(["TRAFFIC TREND — ROAD SAFETY INTELLIGENCE PLATFORM"])
        ws_exec.cell(row=1, column=1).font = title_font
        ws_exec.append([f"Dataset: {dataset_name} | Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}"])
        ws_exec.cell(row=2, column=1).font = sub_font
        ws_exec.append([])

        ws_exec.append(["Key Performance Indicator", "Value", "Benchmark Reference"])
        for col_idx in range(1, 4):
            c = ws_exec.cell(row=4, column=col_idx)
            c.fill = header_fill
            c.font = header_font
            c.alignment = Alignment(horizontal="center" if col_idx > 1 else "left")

        kpi_rows = [
            ("Total Recorded Crashes", kpis.total_accidents, "Total volume within scope"),
            ("Total Fatalities", kpis.total_fatalities, "Persons killed"),
            ("Total Injured Persons", kpis.total_injured, "Persons injured"),
            ("Total Casualties", kpis.total_casualties, "Fatalities + Injuries"),
            ("Fatal Crashes", kpis.fatal_accidents_count, "Crashes resulting in death"),
            ("Non-Fatal Crashes", kpis.non_fatal_accidents_count, "Grievous, Minor, or PDO"),
            ("Fatality Rate per 100 Crashes", f"{kpis.fatality_rate_pct:.2f}%", "Fatality frequency"),
            ("Casualty Rate per Crash", f"{kpis.casualty_rate_per_crash:.2f}", "Severity multiplier"),
            ("Average Crashes per Day", f"{kpis.avg_accidents_per_day:.2f}", "Daily crash incidence"),
            ("Most Affected Region", kpis.most_affected_region, "Top volume concentration"),
            ("Most Affected Time Window", kpis.most_affected_time_window, "Diurnal peak window"),
        ]

        for r_idx, (name, val, ref) in enumerate(kpi_rows, start=5):
            ws_exec.append([name, val, ref])
            for col_idx in range(1, 4):
                ws_exec.cell(row=r_idx, column=col_idx).border = thin_border

        # Tab 2: Filtered Records
        ws_data = wb.create_sheet(title="Accident Records")
        ws_data.views.sheetView[0].showGridLines = True

        export_cols = [c for c in df_filtered.columns if c != "dataset_id"]
        ws_data.append(export_cols)

        for col_idx, col_name in enumerate(export_cols, start=1):
            c = ws_data.cell(row=1, column=col_idx)
            c.fill = sub_fill
            c.font = header_font
            c.alignment = Alignment(horizontal="center")

        for _, row in df_filtered[export_cols].iterrows():
            ws_data.append([str(v) if pd.notna(v) else "" for v in row.values])

        # Auto-adjust column widths
        for ws in [ws_exec, ws_data]:
            for col in ws.columns:
                max_len = max(len(str(cell.value or '')) for cell in col)
                col_letter = get_column_letter(col[0].column)
                ws.column_dimensions[col_letter].width = min(max(max_len + 3, 12), 45)

        wb.save(output_path)
        return output_path
