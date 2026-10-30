"""
Unit Tests for DataCleaner and Profiler
"""
import pytest
import pandas as pd
import numpy as np
from src.data.cleaner import DataCleaner, CleaningOptions
from src.data.profiler import DataProfiler

@pytest.fixture
def dirty_dataframe():
    """Provides synthetic dataframe with duplicates, bad dates, bad coords, and negative casualties."""
    return pd.DataFrame([
        {
            "accident_id": "ACC-001",
            "accident_date": "2023-05-10",
            "state": "Maharashtra",
            "latitude": 19.0760,
            "longitude": 72.8777,
            "accident_severity": "Fatal",
            "fatalities_count": 2,
            "injured_count": 1
        },
        # Duplicate record
        {
            "accident_id": "ACC-001",
            "accident_date": "2023-05-10",
            "state": "Maharashtra",
            "latitude": 19.0760,
            "longitude": 72.8777,
            "accident_severity": "Fatal",
            "fatalities_count": 2,
            "injured_count": 1
        },
        # Bad date record
        {
            "accident_id": "ACC-002",
            "accident_date": "invalid-date-string",
            "state": "Karnataka",
            "latitude": 12.9716,
            "longitude": 77.5946,
            "accident_severity": "Minor Injury",
            "fatalities_count": 0,
            "injured_count": 2
        },
        # Out-of-bounds coordinates & negative casualties
        {
            "accident_id": "ACC-003",
            "accident_date": "2023-08-15",
            "state": "Delhi",
            "latitude": 999.0,  # Invalid
            "longitude": -500.0, # Invalid
            "accident_severity": "Minor Injury",
            "fatalities_count": -5,  # Invalid negative
            "injured_count": 0
        }
    ])

def test_cleaner_deduplication(dirty_dataframe):
    """Verify deduplication removes duplicate records."""
    cleaned, summary = DataCleaner.clean(dirty_dataframe, CleaningOptions(drop_duplicates=True))
    assert summary.duplicates_removed == 1
    assert len(cleaned) < len(dirty_dataframe)

def test_cleaner_invalid_date_dropping(dirty_dataframe):
    """Verify invalid dates are dropped when strategy is 'drop'."""
    cleaned, summary = DataCleaner.clean(dirty_dataframe, CleaningOptions(handle_missing_dates="drop"))
    assert summary.invalid_dates_dropped == 1
    assert "ACC-002" not in cleaned["accident_id"].values

def test_cleaner_coordinate_sanitization(dirty_dataframe):
    """Verify out of range coordinates are coerced to NaN."""
    cleaned, summary = DataCleaner.clean(dirty_dataframe, CleaningOptions(validate_coordinates=True))
    bad_row = cleaned[cleaned["accident_id"] == "ACC-003"].iloc[0]
    assert np.isnan(bad_row["latitude"])
    assert np.isnan(bad_row["longitude"])
    assert summary.invalid_coordinates_nulled >= 2

def test_cleaner_negative_casualty_clamping(dirty_dataframe):
    """Verify negative casualties are clamped to zero."""
    cleaned, summary = DataCleaner.clean(dirty_dataframe, CleaningOptions(enforce_non_negative_casualties=True))
    bad_row = cleaned[cleaned["accident_id"] == "ACC-003"].iloc[0]
    assert bad_row["fatalities_count"] == 0
    assert summary.negative_casualties_corrected >= 1

def test_profiler_scorecard_calculation(dirty_dataframe):
    """Verify mathematically documented scorecard outputs."""
    scorecard = DataProfiler.profile(dirty_dataframe)
    assert 0.0 <= scorecard.overall_score <= 100.0
    assert 0.0 <= scorecard.completeness_score <= 100.0
    assert 0.0 <= scorecard.uniqueness_score <= 100.0
    assert 0.0 <= scorecard.validity_score <= 100.0
    assert 0.0 <= scorecard.consistency_score <= 100.0
    assert scorecard.duplicate_count == 1

