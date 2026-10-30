"""
SQLAlchemy ORM Data Models for TRAFFIC TREND Platform
"""
from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

def utc_now() -> datetime:
    """Returns timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)

class DatasetRecord(Base):
    """Tracks metadata and lifecycle of all imported or demonstration datasets."""
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, autoincrement=True)
    dataset_name = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)  # CSV, XLSX, PARQUET
    source_type = Column(String(50), nullable=False, default="Uploaded")  # Uploaded, Demonstration Benchmark, API Connector
    file_size_bytes = Column(Integer, default=0)
    checksum_sha256 = Column(String(64), nullable=True)
    record_count = Column(Integer, default=0)
    column_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    raw_file_path = Column(String(500), nullable=False)
    processed_file_path = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    # Relationships
    import_history = relationship("ImportHistory", back_populates="dataset", cascade="all, delete-orphan")
    quality_metrics = relationship("DataQualityMetric", back_populates="dataset", cascade="all, delete-orphan")


class ImportHistory(Base):
    """Detailed audit log for dataset intake, deduplication and transformation runs."""
    __tablename__ = "import_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"), nullable=False)
    imported_by = Column(String(100), default="System / Analyst")
    status = Column(String(50), nullable=False, default="SUCCESS")  # SUCCESS, FAILED, WARNING
    original_records = Column(Integer, default=0)
    retained_records = Column(Integer, default=0)
    duplicate_count = Column(Integer, default=0)
    missing_values_handled = Column(Integer, default=0)
    invalid_records_dropped = Column(Integer, default=0)
    execution_time_ms = Column(Float, default=0.0)
    error_message = Column(Text, nullable=True)
    summary_notes = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=utc_now)

    dataset = relationship("DatasetRecord", back_populates="import_history")


class DataQualityMetric(Base):
    """Persisted scorecards evaluating completeness, validity, uniqueness, and consistency."""
    __tablename__ = "data_quality_metrics"

    id = Column(Integer, primary_key=True, autoincrement=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"), nullable=False)
    completeness_score = Column(Float, default=100.0)
    uniqueness_score = Column(Float, default=100.0)
    validity_score = Column(Float, default=100.0)
    consistency_score = Column(Float, default=100.0)
    overall_quality_score = Column(Float, default=100.0)
    duplicate_percentage = Column(Float, default=0.0)
    missing_percentage = Column(Float, default=0.0)
    invalid_date_count = Column(Integer, default=0)
    evaluation_timestamp = Column(DateTime, default=utc_now)

    dataset = relationship("DatasetRecord", back_populates="quality_metrics")


class ProcessingLog(Base):
    """Immutable audit trail for all analytical, pipeline and maintenance operations."""
    __tablename__ = "processing_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    dataset_id = Column(Integer, nullable=True)
    operation = Column(String(100), nullable=False)  # UPLOAD, CLEAN, TRANSFORM, EXPORT, REPORT, REFRESH
    status = Column(String(50), default="INFO")  # INFO, WARNING, ERROR, SUCCESS
    details = Column(Text, nullable=False)
    created_at = Column(DateTime, default=utc_now)
