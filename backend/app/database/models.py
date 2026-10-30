from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from backend.app.database.connection import Base

def utc_now():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    role = Column(String(50), default="analyst", nullable=False)  # admin, analyst, viewer
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utc_now)

class DatasetMetadata(Base):
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(1000), nullable=False)
    row_count = Column(Integer, default=0)
    column_count = Column(Integer, default=0)
    upload_date = Column(DateTime, default=utc_now)
    status = Column(String(50), default="ready")  # uploaded, profiling, cleaning, ready, error
    is_active = Column(Boolean, default=False)
    origin = Column(String(255), default="Manual Upload")
    description = Column(Text, nullable=True)

    records = relationship("AccidentRecord", back_populates="dataset", cascade="all, delete-orphan")
    quality_reports = relationship("DataQualityReport", back_populates="dataset", cascade="all, delete-orphan")

class AccidentRecord(Base):
    __tablename__ = "accident_records"

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Identification
    accident_id = Column(String(100), index=True)
    accident_date = Column(String(50), index=True)
    accident_time = Column(String(50), nullable=True)
    
    # Temporal
    year = Column(Integer, index=True, nullable=True)
    month = Column(String(50), index=True, nullable=True)
    day_of_week = Column(String(50), index=True, nullable=True)
    hour_of_day = Column(Integer, index=True, nullable=True)
    
    # Geographical
    state = Column(String(100), index=True, nullable=True)
    district = Column(String(100), index=True, nullable=True)
    location_type = Column(String(50), nullable=True)  # Urban, Rural, Semi-Urban
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    
    # Road and Environmental Conditions
    road_type = Column(String(100), nullable=True)
    road_condition = Column(String(100), nullable=True)
    weather = Column(String(100), nullable=True)
    light_condition = Column(String(100), nullable=True)
    
    # Severity & Casualties
    accident_severity = Column(String(100), index=True, nullable=True)  # Fatal, Grievous Injury, Minor Injury, Property Damage Only
    fatalities_count = Column(Integer, default=0)
    injured_count = Column(Integer, default=0)
    vehicles_involved_count = Column(Integer, default=1)
    
    # Classification
    collision_type = Column(String(100), nullable=True)
    primary_vehicle_type = Column(String(100), nullable=True)
    contributing_factor = Column(String(255), nullable=True)
    data_origin = Column(String(255), nullable=True)

    dataset = relationship("DatasetMetadata", back_populates="records")

    __table_args__ = (
        Index("idx_accidents_state_year", "state", "year"),
        Index("idx_accidents_severity_date", "accident_severity", "accident_date"),
    )

class DataQualityReport(Base):
    __tablename__ = "data_quality_reports"

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False)
    total_records = Column(Integer, default=0)
    missing_cells = Column(Integer, default=0)
    duplicate_rows = Column(Integer, default=0)
    anomaly_count = Column(Integer, default=0)
    quality_score = Column(Float, default=100.0)
    metrics_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)

    dataset = relationship("DatasetMetadata", back_populates="quality_reports")

class ReportHistory(Base):
    __tablename__ = "report_history"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    report_type = Column(String(50), default="executive")  # executive, geographical, severity, risk
    date_range_start = Column(String(50), nullable=True)
    date_range_end = Column(String(50), nullable=True)
    file_path = Column(String(1000), nullable=False)
    format = Column(String(20), default="pdf")  # pdf, excel, csv
    generated_at = Column(DateTime, default=utc_now)
    status = Column(String(50), default="completed")

class ProcessingLog(Base):
    __tablename__ = "processing_logs"

    id = Column(Integer, primary_key=True, index=True)
    level = Column(String(20), default="INFO")
    message = Column(Text, nullable=False)
    module = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=utc_now)
