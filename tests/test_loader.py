"""
Unit Tests for DataLoader and Schema Mapper
"""
import pytest
import pandas as pd
from pathlib import Path
from src.data.loader import DataLoader
from src.utils.configuration import CONFIG

def test_load_csv_benchmark():
    """Verify loading valid CSV dataset."""
    assert CONFIG.BENCHMARK_DEMO_PATH.exists()
    df, meta = DataLoader.load_file(CONFIG.BENCHMARK_DEMO_PATH)
    assert not df.empty
    assert len(df) == 3500
    assert meta["file_type"] == "CSV"
    assert "detected_mappings" in meta
    assert meta["detected_mappings"]["state"] == "state"

def test_load_excel_benchmark():
    """Verify loading valid Excel (.xlsx) dataset."""
    assert CONFIG.BENCHMARK_DEMO_EXCEL.exists()
    df, meta = DataLoader.load_file(CONFIG.BENCHMARK_DEMO_EXCEL)
    assert not df.empty
    assert len(df) == 3500
    assert meta["file_type"] == "XLSX"

def test_unsupported_file_extension(tmp_path):
    """Verify ValueError is raised on unsupported extensions."""
    bad_file = tmp_path / "data.docx"
    bad_file.write_text("invalid content")
    with pytest.raises(ValueError, match="Unsupported file format"):
        DataLoader.load_file(bad_file)

