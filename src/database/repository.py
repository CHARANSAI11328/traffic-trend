"""
Repository Pattern Implementation for TRAFFIC TREND Platform
Decouples raw database transactions from application services.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from src.database.models import DatasetRecord, ImportHistory, DataQualityMetric, ProcessingLog
from src.database.connection import get_db_session
from src.monitoring.logger import logger

class DatasetRepository:
    """Repository handling CRUD operations for datasets and import metadata."""

    @staticmethod
    def register_dataset(
        name: str,
        file_type: str,
        source_type: str,
        file_size_bytes: int,
        raw_path: str,
        processed_path: Optional[str] = None,
        record_count: int = 0,
        column_count: int = 0,
        checksum: Optional[str] = None
    ) -> DatasetRecord:
        """Registers a new dataset or updates active pointer."""
        with get_db_session() as session:
            # Check if record with exact checksum already exists
            existing = None
            if checksum:
                existing = session.query(DatasetRecord).filter_by(checksum_sha256=checksum).first()

            if existing:
                existing.dataset_name = name
                existing.record_count = record_count
                existing.column_count = column_count
                existing.processed_file_path = processed_path or existing.processed_file_path
                existing.updated_at = datetime.now(timezone.utc)
                session.add(existing)
                logger.info(f"Updated existing dataset metadata: ID {existing.id} ({name})")
                return existing
            
            # Deactivate previous active markers if setting a new active dataset
            new_record = DatasetRecord(
                dataset_name=name,
                file_type=file_type.upper(),
                source_type=source_type,
                file_size_bytes=file_size_bytes,
                checksum_sha256=checksum,
                record_count=record_count,
                column_count=column_count,
                is_active=True,
                raw_file_path=raw_path,
                processed_file_path=processed_path,
                created_at=datetime.now(timezone.utc)
            )
            session.add(new_record)
            session.flush()
            logger.info(f"Registered new dataset: ID {new_record.id} ({name})")
            return new_record

    @staticmethod
    def get_all_datasets() -> List[Dict[str, Any]]:
        """Retrieves list of all registered datasets."""
        with get_db_session() as session:
            records = session.query(DatasetRecord).order_by(DatasetRecord.created_at.desc()).all()
            return [
                {
                    "id": r.id,
                    "dataset_name": r.dataset_name,
                    "file_type": r.file_type,
                    "source_type": r.source_type,
                    "file_size_bytes": r.file_size_bytes,
                    "record_count": r.record_count,
                    "column_count": r.column_count,
                    "is_active": r.is_active,
                    "raw_file_path": r.raw_file_path,
                    "processed_file_path": r.processed_file_path,
                    "checksum_sha256": r.checksum_sha256,
                    "created_at": r.created_at,
                    "updated_at": r.updated_at
                }
                for r in records
            ]

    @staticmethod
    def get_active_dataset() -> Optional[Dict[str, Any]]:
        """Retrieves currently active dataset metadata."""
        with get_db_session() as session:
            record = session.query(DatasetRecord).filter_by(is_active=True).order_by(DatasetRecord.updated_at.desc()).first()
            if not record:
                record = session.query(DatasetRecord).order_by(DatasetRecord.created_at.desc()).first()
            if record:
                return {
                    "id": record.id,
                    "dataset_name": record.dataset_name,
                    "file_type": record.file_type,
                    "source_type": record.source_type,
                    "file_size_bytes": record.file_size_bytes,
                    "record_count": record.record_count,
                    "column_count": record.column_count,
                    "is_active": record.is_active,
                    "raw_file_path": record.raw_file_path,
                    "processed_file_path": record.processed_file_path,
                    "checksum_sha256": record.checksum_sha256,
                    "created_at": record.created_at,
                    "updated_at": record.updated_at
                }
            return None

    @staticmethod
    def set_active_dataset(dataset_id: int) -> bool:
        """Sets a specific dataset as the active platform source."""
        with get_db_session() as session:
            session.query(DatasetRecord).update({"is_active": False})
            target = session.query(DatasetRecord).filter_by(id=dataset_id).first()
            if target:
                target.is_active = True
                target.updated_at = datetime.now(timezone.utc)
                logger.info(f"Dataset ID {dataset_id} set as active.")
                return True
            return False

    @staticmethod
    def record_import_event(
        dataset_id: int,
        status: str,
        original_records: int,
        retained_records: int,
        duplicate_count: int = 0,
        missing_values_handled: int = 0,
        invalid_records_dropped: int = 0,
        execution_time_ms: float = 0.0,
        error_message: Optional[str] = None,
        summary_notes: Optional[str] = None
    ) -> None:
        """Logs an ingestion or transformation event in import history."""
        with get_db_session() as session:
            event = ImportHistory(
                dataset_id=dataset_id,
                status=status.upper(),
                original_records=original_records,
                retained_records=retained_records,
                duplicate_count=duplicate_count,
                missing_values_handled=missing_values_handled,
                invalid_records_dropped=invalid_records_dropped,
                execution_time_ms=execution_time_ms,
                error_message=error_message,
                summary_notes=summary_notes,
                timestamp=datetime.now(timezone.utc)
            )
            session.add(event)

    @staticmethod
    def get_import_history(limit: int = 50) -> List[Dict[str, Any]]:
        """Returns recent import audit events."""
        with get_db_session() as session:
            records = session.query(ImportHistory).order_by(ImportHistory.timestamp.desc()).limit(limit).all()
            return [
                {
                    "id": r.id,
                    "dataset_id": r.dataset_id,
                    "status": r.status,
                    "original_records": r.original_records,
                    "retained_records": r.retained_records,
                    "duplicate_count": r.duplicate_count,
                    "missing_values_handled": r.missing_values_handled,
                    "invalid_records_dropped": r.invalid_records_dropped,
                    "execution_time_ms": r.execution_time_ms,
                    "error_message": r.error_message,
                    "summary_notes": r.summary_notes,
                    "timestamp": r.timestamp
                }
                for r in records
            ]

    @staticmethod
    def save_quality_metrics(
        dataset_id: int,
        completeness: float,
        uniqueness: float,
        validity: float,
        consistency: float,
        overall: float,
        duplicate_pct: float,
        missing_pct: float,
        invalid_date_count: int
    ) -> None:
        """Stores a calculated data quality scorecard."""
        with get_db_session() as session:
            metric = DataQualityMetric(
                dataset_id=dataset_id,
                completeness_score=completeness,
                uniqueness_score=uniqueness,
                validity_score=validity,
                consistency_score=consistency,
                overall_quality_score=overall,
                duplicate_percentage=duplicate_pct,
                missing_percentage=missing_pct,
                invalid_date_count=invalid_date_count,
                evaluation_timestamp=datetime.now(timezone.utc)
            )
            session.add(metric)

    @staticmethod
    def get_latest_quality_metrics(dataset_id: int) -> Optional[Dict[str, Any]]:
        """Retrieves most recent quality metrics scorecard for a dataset."""
        with get_db_session() as session:
            metric = session.query(DataQualityMetric).filter_by(dataset_id=dataset_id).order_by(DataQualityMetric.evaluation_timestamp.desc()).first()
            if metric:
                return {
                    "id": metric.id,
                    "dataset_id": metric.dataset_id,
                    "completeness_score": metric.completeness_score,
                    "uniqueness_score": metric.uniqueness_score,
                    "validity_score": metric.validity_score,
                    "consistency_score": metric.consistency_score,
                    "overall_quality_score": metric.overall_quality_score,
                    "duplicate_percentage": metric.duplicate_percentage,
                    "missing_percentage": metric.missing_percentage,
                    "invalid_date_count": metric.invalid_date_count,
                    "evaluation_timestamp": metric.evaluation_timestamp
                }
            return None

    @staticmethod
    def log_operation(operation: str, details: str, status: str = "INFO", dataset_id: Optional[int] = None) -> None:
        """Records an operational audit log entry."""
        with get_db_session() as session:
            log_entry = ProcessingLog(
                dataset_id=dataset_id,
                operation=operation.upper(),
                details=details,
                status=status.upper(),
                created_at=datetime.now(timezone.utc)
            )
            session.add(log_entry)

    @staticmethod
    def get_recent_logs(limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieves recent system and processing logs."""
        with get_db_session() as session:
            logs = session.query(ProcessingLog).order_by(ProcessingLog.created_at.desc()).limit(limit).all()
            return [
                {
                    "id": l.id,
                    "dataset_id": l.dataset_id,
                    "operation": l.operation,
                    "status": l.status,
                    "details": l.details,
                    "created_at": l.created_at
                }
                for l in logs
            ]
