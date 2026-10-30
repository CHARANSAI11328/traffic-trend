"""
Executive PDF Report Generator for TRAFFIC TREND Platform
Generates institutional road safety intelligence reports with tables, KPIs and audit trails.
"""
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
from src.utils.configuration import EXPORTS_DIR, AppConfig
from src.monitoring.logger import logger

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
        """Builds multi-section PDF document and writes to disk."""
        if output_path is None:
            ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            output_path = EXPORTS_DIR / f"Traffic_Trend_Executive_Report_{ts}.pdf"

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
        
        # Custom styles
        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Heading1"],
            fontSize=22,
            leading=26,
            textColor=colors.HexColor("#0f172a"),
            fontName="Helvetica-Bold"
        )
        subtitle_style = ParagraphStyle(
            "DocSubTitle",
            parent=styles["Normal"],
            fontSize=11,
            leading=14,
            textColor=colors.HexColor("#475569"),
            fontName="Helvetica"
        )
        h2_style = ParagraphStyle(
            "H2Style",
            parent=styles["Heading2"],
            fontSize=13,
            leading=17,
            textColor=colors.HexColor("#1e293b"),
            fontName="Helvetica-Bold"
        )
        body_style = ParagraphStyle(
            "Body",
            parent=styles["Normal"],
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#334155")
        )
        small_style = ParagraphStyle(
            "SmallBody",
            parent=styles["Normal"],
            fontSize=8,
            leading=11,
            textColor=colors.HexColor("#64748b")
        )

        story = []

        # 1. Header Banner
        story.append(Paragraph("TRAFFIC TREND", title_style))
        story.append(Paragraph("Road Accident Data Analysis & Intelligence Platform — Executive Brief", subtitle_style))
        story.append(Spacer(1, 10))
        story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#2563eb"), spaceAfter=12))

        # 2. Metadata Block
        meta_data = [
            [
                Paragraph(f"<b>Active Dataset:</b> {dataset_name}", body_style),
                Paragraph(f"<b>Generated On:</b> {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}", body_style)
            ],
            [
                Paragraph(f"<b>Filter Scope:</b> {filter_summary}", body_style),
                Paragraph(f"<b>Record Count:</b> {len(df_filtered):,} incidents", body_style)
            ]
        ]
        meta_table = Table(meta_data, colWidths=[270, 270])
        meta_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
            ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#e2e8f0")),
            ('PADDING', (0,0), (-1,-1), 6),
        ]))
        story.append(meta_table)
        story.append(Spacer(1, 16))

        # 3. Key Performance Indicators Section
        story.append(Paragraph("1. Executive Summary & Core Safety KPIs", h2_style))
        story.append(Spacer(1, 6))

        kpi_table_data = [
            ["Metric Dimension", "Value", "Metric Dimension", "Value"],
            ["Total Recorded Incidents", f"{kpis.total_accidents:,}", "Total Fatalities", f"{kpis.total_fatalities:,}"],
            ["Fatal Crash Count", f"{kpis.fatal_accidents_count:,}", "Total Injured Persons", f"{kpis.total_injured:,}"],
            ["Non-Fatal Crash Count", f"{kpis.non_fatal_accidents_count:,}", "Total Casualties", f"{kpis.total_casualties:,}"],
            ["Fatality Rate (% of crashes)", f"{kpis.fatality_rate_pct:.1f}%", "Casualties per Crash", f"{kpis.casualty_rate_per_crash:.2f}"],
            ["Most Affected Region", str(kpis.most_affected_region), "Peak Time Window", str(kpis.most_affected_time_window)]
        ]
        kpi_table = Table(kpi_table_data, colWidths=[150, 120, 150, 120])
        kpi_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0f172a")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8.5),
            ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
            ('ALIGN', (3, 1), (3, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#f1f5f9")]),
            ('PADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(kpi_table)
        story.append(Spacer(1, 16))

        # 4. Regional Distribution Breakdown (Top 5)
        story.append(Paragraph("2. High-Density Regional Concentrations (Top 5)", h2_style))
        story.append(Spacer(1, 6))

        geo_col = next((c for c in ["state", "district", "city"] if c in df_filtered.columns), None)
        if geo_col:
            top_geo = df_filtered[geo_col].value_counts().head(5).reset_index()
            top_geo.columns = ["Region", "Crash Count"]
            top_geo_data = [["Rank", "Administrative Region", "Recorded Crashes", "% Share"]]
            total_n = len(df_filtered)
            for i, row in top_geo.iterrows():
                share = (row["Crash Count"] / total_n * 100) if total_n > 0 else 0
                top_geo_data.append([str(i+1), str(row["Region"]), f"{row['Crash Count']:,}", f"{share:.1f}%"])

            geo_table = Table(top_geo_data, colWidths=[40, 260, 120, 120])
            geo_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#1e293b")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8.5),
                ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ('PADDING', (0, 0), (-1, -1), 5),
            ]))
            story.append(geo_table)
        else:
            story.append(Paragraph("Regional geographic fields not available in active filtered dataset.", small_style))

        story.append(Spacer(1, 16))

        # 5. Methodological Notes and Disclaimers
        story.append(Paragraph("3. Analytical Methodology & Governance Disclaimers", h2_style))
        story.append(Spacer(1, 6))
        disclaimer_text = (
            "<b>Methodology Note:</b> This document is automatically synthesized by the TRAFFIC TREND platform. "
            "Metrics are computed exclusively from valid records matching current active filter constraints. "
            "Fatality rates represent recorded deaths per 100 reported crashes. "
            "Correlations and risk indices designate empirical statistical associations and should not be construed as verified causal mechanisms. "
            "Data integrity relies on primary reporting from police, transportation departments, or institutional logs."
        )
        story.append(Paragraph(disclaimer_text, small_style))

        # Build PDF
        doc.build(story)
        logger.info(f"Executive PDF generated at: {output_path}")
        return output_path
