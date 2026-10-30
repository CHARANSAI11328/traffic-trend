"""
Unit Tests for Database Connection, Models, and Repository Pattern
"""
import pytest
from src.database.connection import init_db, check_database_health
from src.database.repository import DatasetRepository

def test_database_initialization():
    """Verify tables are created and engine is healthy."""
    init_db()
    health = check_database_health()
    assert health["status"] == "HEALTHY"
    assert health["connected"] is True
    assert health["latency_ms"] >= 0

def test_dataset_registration_and_activation(tmp_path):
    """Verify registration, retrieval, and active flag toggling."""
    dummy_file = tmp_path / "test_accidents.csv"
    dummy_file.write_text("id,date\n1,2023-01-01")
    
    record = DatasetRepository.register_dataset(
        name="test_accidents.csv",
        file_type="CSV",
        source_type="Uploaded",
        file_size_bytes=len(dummy_file.read_bytes()),
        raw_path=str(dummy_file),
        record_count=1,
        column_count=2,
        checksum="test_hash_123"
    )
    assert record.id is not None
    
    # Verify retrieval
    active = DatasetRepository.get_active_dataset()
    assert active is not None
    assert active["dataset_name"] == "test_accidents.csv"

def test_import_history_logging():
    """Verify audit events are persisted and queried."""
    DatasetRepository.record_import_event(
        dataset_id=1,
        status="SUCCESS",
        original_records=100,
        retained_records=95,
        duplicate_count=5,
        summary_notes="Test import event."
    )
    history = DatasetRepository.get_import_history(limit=5)
    assert len(history) > 0
    assert history[0]["original_records"] == 100

