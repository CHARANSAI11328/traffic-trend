"""
Multi-Tab Excel Intelligence Exporter for TRAFFIC TREND Platform
Generates formatted Excel workbooks with executive summaries and analytical aggregates.
"""
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, Optional
import io
import pandas as pd
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from src.utils.configuration import EXPORTS_DIR
from src.monitoring.logger import logger

class ExcelExporter:
    """Builds presentation-ready multi-sheet Excel intelligence workbooks."""

    @classmethod
    def export_workbook(
        cls,
        kpis: Any,
        df_filtered: pd.DataFrame,
        dataset_name: str,
        output_path: Optional[Path] = None
    ) -> Path:
        """Assembles workbook across 5 standardized analytical worksheets."""
        if output_path is None:
            ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            output_path = EXPORTS_DIR / f"Traffic_Trend_Intelligence_{ts}.xlsx"

        output_path.parent.mkdir(parents=True, exist_ok=True)
        wb = openpyxl.Workbook()

        # Styles
        navy_fill = PatternFill(start_color="0F172A", end_color="0F172A", fill_type="solid")
        cyan_fill = PatternFill(start_color="0284C7", end_color="0284C7", fill_type="solid")
        header_font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
        title_font = Font(name="Calibri", size=14, bold=True, color="0F172A")
        bold_font = Font(name="Calibri", size=11, bold=True)
        thin_border = Border(
            left=Side(style='thin', color='E2E8F0'),
            right=Side(style='thin', color='E2E8F0'),
            top=Side(style='thin', color='E2E8F0'),
            bottom=Side(style='thin', color='E2E8F0')
        )

        # ----------------------------------------------------
        # SHEET 1: EXECUTIVE SUMMARY
        # ----------------------------------------------------
        ws1 = wb.active
        ws1.title = "Executive Summary"
        ws1.views.sheetView[0].showGridLines = True

        ws1.cell(row=1, column=1, value="TRAFFIC TREND — ROAD ACCIDENT INTELLIGENCE").font = title_font
        ws1.cell(row=2, column=1, value=f"Dataset: {dataset_name} | Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
        
        ws1.cell(row=4, column=1, value="Core Metric").fill = navy_fill
        ws1.cell(row=4, column=1).font = header_font
        ws1.cell(row=4, column=2, value="Current Value").fill = navy_fill
        ws1.cell(row=4, column=2).font = header_font
        ws1.cell(row=4, column=3, value="Analytical Context").fill = navy_fill
        ws1.cell(row=4, column=3).font = header_font

        kpi_rows = [
            ("Total Recorded Incidents", kpis.total_accidents, "Total volume of filtered accident incidents"),
            ("Total Fatalities", kpis.total_fatalities, "Sum of recorded deaths"),
            ("Total Injured Persons", kpis.total_injured, "Sum of grievous and minor injuries"),
            ("Total Casualties", kpis.total_casualties, "Combined fatalities and injuries"),
            ("Fatal Crashes Count", kpis.fatal_accidents_count, "Crashes resulting in at least 1 fatality"),
            ("Non-Fatal Crashes Count", kpis.non_fatal_accidents_count, "Crashes with injuries or property damage only"),
            ("Fatality Rate", f"{kpis.fatality_rate_pct:.1f}%", "Recorded deaths per 100 crashes"),
            ("Casualty Rate per Crash", kpis.casualty_rate_per_crash, "Average casualties (dead + injured) per crash"),
            ("Most Affected Region", str(kpis.most_affected_region), "Administrative jurisdiction with highest crash count"),
            ("Peak Time Window", str(kpis.most_affected_time_window), "Time block recording highest collision volume")
        ]

        for idx, (m, v, ctx) in enumerate(kpi_rows, start=5):
            ws1.cell(row=idx, column=1, value=m).font = bold_font
            ws1.cell(row=idx, column=2, value=v)
            ws1.cell(row=idx, column=3, value=ctx)
            for c in range(1, 4):
                ws1.cell(row=idx, column=c).border = thin_border

        # ----------------------------------------------------
        # SHEET 2: REGIONAL BREAKDOWN
        # ----------------------------------------------------
        geo_col = next((c for c in ["state", "district", "city"] if c in df_filtered.columns), None)
        if geo_col:
            ws2 = wb.create_sheet(title="Regional Breakdown")
            ws2.views.sheetView[0].showGridLines = True
            
            geo_df = df_filtered.groupby(geo_col).agg(
                Crashes=("accident_id" if "accident_id" in df_filtered.columns else geo_col, "count"),
                Fatalities=("fatalities_count", lambda x: pd.to_numeric(x, errors="coerce").fillna(0).sum()) if "fatalities_count" in df_filtered.columns else (geo_col, lambda x: 0),
                Injuries=("injured_count", lambda x: pd.to_numeric(x, errors="coerce").fillna(0).sum()) if "injured_count" in df_filtered.columns else (geo_col, lambda x: 0)
            ).reset_index().sort_values("Crashes", ascending=False)

            headers = ["Region", "Total Crashes", "Fatalities", "Injured", "Fatality Rate (%)"]
            for col_idx, h in enumerate(headers, start=1):
                cell = ws2.cell(row=1, column=col_idx, value=h)
                cell.fill = navy_fill
                cell.font = header_font

            for row_idx, r in enumerate(geo_df.itertuples(index=False), start=2):
                fat_rate = round((r.Fatalities / r.Crashes * 100), 1) if r.Crashes > 0 else 0
                ws2.cell(row=row_idx, column=1, value=str(r[0]))
                ws2.cell(row=row_idx, column=2, value=r.Crashes)
                ws2.cell(row=row_idx, column=3, value=r.Fatalities)
                ws2.cell(row=row_idx, column=4, value=r.Injuries)
                ws2.cell(row=row_idx, column=5, value=fat_rate)
                for c in range(1, 6):
                    ws2.cell(row=row_idx, column=c).border = thin_border

        # ----------------------------------------------------
        # SHEET 3: FILTERED DATA EXTRACT (UP TO 10,000 ROWS)
        # ----------------------------------------------------
        ws3 = wb.create_sheet(title="Filtered Incident Records")
        ws3.views.sheetView[0].showGridLines = True
        
        sample_df = df_filtered.head(10000)
        cols = list(sample_df.columns)
        
        for col_idx, col_name in enumerate(cols, start=1):
            cell = ws3.cell(row=1, column=col_idx, value=str(col_name))
            cell.fill = cyan_fill
            cell.font = header_font

        for row_idx, row_values in enumerate(sample_df.itertuples(index=False), start=2):
            for col_idx, val in enumerate(row_values, start=1):
                # Clean NaNs or Timestamps for openpyxl
                if pd.isna(val):
                    clean_val = ""
                elif isinstance(val, pd.Timestamp):
                    clean_val = val.strftime("%Y-%m-%d %H:%M:%S")
                else:
                    clean_val = val
                ws3.cell(row=row_idx, column=col_idx, value=clean_val)

        # Autofit column widths across all sheets
        for ws in wb.worksheets:
            for col in ws.columns:
                max_len = max(len(str(cell.value or '')) for cell in col[:100])
                col_letter = get_column_letter(col[0].column)
                ws.column_dimensions[col_letter].width = max(max_len + 3, 12)

        wb.save(str(output_path))
        logger.info(f"Excel workbook exported to: {output_path}")
        return output_path
