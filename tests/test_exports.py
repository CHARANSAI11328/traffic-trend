"""
Unit Tests for Report Generation (PDF and Excel)
"""
import pytest
import pandas as pd
from pathlib import Path
from src.analytics.kpis import KPICalculator
from src.reports.pdf_generator import PDFReportGenerator
from src.reports.excel_exporter import ExcelExporter

@pytest.fixture
def test_export_data():
    """Provides sample dataframe and KPIs for report compilation."""
    df = pd.DataFrame({
        "accident_id": ["ACC-1", "ACC-2"],
        "accident_date": ["2023-01-01", "2023-01-02"],
        "state": ["Maharashtra", "Karnataka"],
        "district": ["Mumbai", "Bengaluru"],
        "accident_severity": ["Fatal", "Minor Injury"],
        "fatalities_count": [1, 0],
        "injured_count": [0, 2]
    })
    kpis = KPICalculator.compute(df)
    return df, kpis

def test_generate_pdf_report(tmp_path, test_export_data):
    """Verify ReportLab compiles valid PDF without crashing."""
    df, kpis = test_export_data
    out_pdf = tmp_path / "test_report.pdf"
    res_path = PDFReportGenerator.generate_executive_report(
        kpis=kpis,
        df_filtered=df,
        dataset_name="Test Dataset",
        output_path=out_pdf
    )
    assert res_path.exists()
    assert res_path.stat().st_size > 1000  # Non-trivial PDF size

def test_generate_excel_workbook(tmp_path, test_export_data):
    """Verify OpenPyXL builds multi-sheet Excel file."""
    df, kpis = test_export_data
    out_xlsx = tmp_path / "test_workbook.xlsx"
    res_path = ExcelExporter.export_workbook(
        kpis=kpis,
        df_filtered=df,
        dataset_name="Test Dataset",
        output_path=out_xlsx
    )
    assert res_path.exists()
    assert res_path.stat().st_size > 1000

