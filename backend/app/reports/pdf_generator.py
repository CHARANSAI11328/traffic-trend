from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, Any, Optional
import io
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from backend.app.core.config import settings

class PDFReportGenerator:
    """Creates printable PDF intelligence briefs."""

    @classmethod
    def generate_executive_report(
        cls,
        kpis: Any,
        df_filtered: pd.DataFrame,
        dataset_name: str,
        filter_summary: str = "All records included",
        output_path: Optional[Path] = None
    ) -> Path:
        if output_path is None:
            ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            output_path = settings.EXPORTS_DATA_DIR / f"Traffic_Trend_Executive_Report_{ts}.pdf"

        output_path.parent.mkdir(parents=True, exist_ok=True)
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Heading1"],
            fontSize=20,
            leading=24,
            textColor=colors.HexColor("#0f172a"),
            fontName="Helvetica-Bold"
        )
        subtitle_style = ParagraphStyle(
            "DocSubTitle",
            parent=styles["Normal"],
            fontSize=10,
            leading=13,
            textColor=colors.HexColor("#475569"),
            fontName="Helvetica"
        )
        h2_style = ParagraphStyle(
            "H2Style",
            parent=styles["Heading2"],
            fontSize=12,
            leading=16,
            textColor=colors.HexColor("#1e293b"),
            fontName="Helvetica-Bold"
        )
        body_style = ParagraphStyle(
            "DocBody",
            parent=styles["Normal"],
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#334155")
        )

        elements = []

        # 1. Header
        elements.append(Paragraph("TRAFFIC TREND", title_style))
        elements.append(Paragraph("ROAD SAFETY INTELLIGENCE PLATFORM — EXECUTIVE ANALYTICAL BRIEF", subtitle_style))
        elements.append(Paragraph(f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')} | Dataset: {dataset_name}", subtitle_style))
        elements.append(Paragraph(f"Scope: {filter_summary}", subtitle_style))
        elements.append(Spacer(1, 12))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cbd5e1"), spaceAfter=15))

        # 2. Executive KPIs Table
        elements.append(Paragraph("1. EXECUTIVE KEY PERFORMANCE INDICATORS", h2_style))
        elements.append(Spacer(1, 6))

        kpi_data = [
            ["Metric", "Value", "Metric", "Value"],
            ["Total Recorded Crashes", f"{kpis.total_accidents:,}", "Total Fatalities", f"{kpis.total_fatalities:,}"],
            ["Total Injured Persons", f"{kpis.total_injured:,}", "Total Casualties", f"{kpis.total_casualties:,}"],
            ["Fatality Rate per 100 Crashes", f"{kpis.fatality_rate_pct:.2f}%", "Fatal Crash Ratio", f"{kpis.fatal_accidents_ratio_pct:.2f}%"],
            ["Average Crashes / Day", f"{kpis.avg_accidents_per_day:.2f}", "Most Impacted Region", str(kpis.most_affected_region)],
        ]

        kpi_table = Table(kpi_data, colWidths=[150, 110, 150, 130])
        kpi_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0f172a")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#f8fafc"), colors.white]),
        ]))
        elements.append(kpi_table)
        elements.append(Spacer(1, 15))

        # 3. Regional Crash Ranking
        if "state" in df_filtered.columns and not df_filtered.empty:
            elements.append(Paragraph("2. REGIONAL CRASH DENSITY & SEVERITY (TOP 8)", h2_style))
            elements.append(Spacer(1, 6))

            state_agg = df_filtered.groupby("state").agg(
                crashes=("accident_id" if "accident_id" in df_filtered.columns else "state", "count"),
                fatalities=("fatalities_count", lambda x: pd.to_numeric(x, errors="coerce").fillna(0).sum()) if "fatalities_count" in df_filtered.columns else ("state", lambda x: 0),
                injuries=("injured_count", lambda x: pd.to_numeric(x, errors="coerce").fillna(0).sum()) if "injured_count" in df_filtered.columns else ("state", lambda x: 0)
            ).reset_index().sort_values("crashes", ascending=False).head(8)

            table_rows = [["State / Region", "Accidents", "Fatalities", "Injuries", "Fatality Rate (%)"]]
            for _, r in state_agg.iterrows():
                fr = (r["fatalities"] / r["crashes"] * 100.0) if r["crashes"] > 0 else 0.0
                table_rows.append([
                    str(r["state"]),
                    f"{r['crashes']:,}",
                    f"{r['fatalities']:,}",
                    f"{r['injuries']:,}",
                    f"{fr:.2f}%"
                ])

            state_table = Table(table_rows, colWidths=[180, 85, 85, 85, 105])
            state_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#334155")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor("#f8fafc"), colors.white]),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
            ]))
            elements.append(state_table)
            elements.append(Spacer(1, 15))

        # 4. Methodology & Data Limitations
        elements.append(Paragraph("3. METHODOLOGY, INTEGRITY & DATA LIMITATIONS", h2_style))
        elements.append(Spacer(1, 4))
        elements.append(Paragraph(
            "• <b>Distinction of Casualties:</b> Accident count represents distinct crash events; fatality and injury counts represent human impact figures.<br/>"
            "• <b>Risk Interpretation:</b> Raw crash frequencies reflect recorded volume and should not be equated with road hazard rates without traffic volume or exposure normalization.<br/>"
            "• <b>Data Provenance:</b> All metrics derived from verified ingested database tables without manual fabrication or synthetic inflation.",
            body_style
        ))

        doc.build(elements)
        return output_path
