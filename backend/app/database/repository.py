import json
import logging
from typing import List, Optional, Dict, Any, Tuple
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, or_
from backend.app.database.models import (
    User, DatasetMetadata, AccidentRecord, DataQualityReport, ReportHistory, ProcessingLog
)

logger = logging.getLogger(__name__)

class DatabaseRepository:
    def __init__(self, db: Session):
        self.db = db

    # ------------------ Logging ------------------
    def log(self, level: str, message: str, module: str = "System"):
        try:
            log_entry = ProcessingLog(level=level, message=message, module=module)
            self.db.add(log_entry)
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            logger.error("Failed to write processing log: %s", e)

    def get_recent_logs(self, limit: int = 50) -> List[ProcessingLog]:
        return self.db.query(ProcessingLog).order_by(desc(ProcessingLog.created_at)).limit(limit).all()

    # ------------------ Users ------------------
    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def create_user(self, email: str, hashed_password: str, full_name: Optional[str] = None, role: str = "analyst") -> User:
        user = User(
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            role=role,
            is_active=True
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    # ------------------ Datasets ------------------
    def get_datasets(self) -> List[DatasetMetadata]:
        return self.db.query(DatasetMetadata).order_by(desc(DatasetMetadata.upload_date)).all()

    def get_dataset_by_id(self, dataset_id: int) -> Optional[DatasetMetadata]:
        return self.db.query(DatasetMetadata).filter(DatasetMetadata.id == dataset_id).first()

    def get_active_dataset(self) -> Optional[DatasetMetadata]:
        active = self.db.query(DatasetMetadata).filter(DatasetMetadata.is_active == True).first()
        if not active:
            # Fall back to the most recent ready dataset
            active = self.db.query(DatasetMetadata).filter(DatasetMetadata.status == "ready").order_by(desc(DatasetMetadata.upload_date)).first()
            if active:
                active.is_active = True
                self.db.commit()
        return active

    def set_active_dataset(self, dataset_id: int) -> Optional[DatasetMetadata]:
        self.db.query(DatasetMetadata).update({DatasetMetadata.is_active: False})
        dataset = self.get_dataset_by_id(dataset_id)
        if dataset:
            dataset.is_active = True
            self.db.commit()
            self.db.refresh(dataset)
        return dataset

    def create_dataset(
        self,
        name: str,
        filename: str,
        file_path: str,
        row_count: int,
        column_count: int,
        origin: str = "Manual Upload",
        description: Optional[str] = None,
        is_active: bool = False
    ) -> DatasetMetadata:
        dataset = DatasetMetadata(
            name=name,
            filename=filename,
            file_path=file_path,
            row_count=row_count,
            column_count=column_count,
            origin=origin,
            description=description,
            is_active=is_active,
            status="ready"
        )
        self.db.add(dataset)
        self.db.commit()
        self.db.refresh(dataset)
        return dataset

    def delete_dataset(self, dataset_id: int) -> bool:
        dataset = self.get_dataset_by_id(dataset_id)
        if dataset:
            self.db.delete(dataset)
            self.db.commit()
            return True
        return False

    # ------------------ Records Ingestion ------------------
    def bulk_insert_records(self, dataset_id: int, df: pd.DataFrame, batch_size: int = 1000):
        """Batch inserts accident records from a Pandas DataFrame into the database."""
        records = []
        for _, row in df.iterrows():
            record = AccidentRecord(
                dataset_id=dataset_id,
                accident_id=str(row.get("accident_id", "")),
                accident_date=str(row.get("accident_date", "")),
                accident_time=str(row.get("accident_time", "")) if pd.notna(row.get("accident_time")) else None,
                year=int(row.get("year")) if pd.notna(row.get("year")) else None,
                month=str(row.get("month", "")) if pd.notna(row.get("month")) else None,
                day_of_week=str(row.get("day_of_week", "")) if pd.notna(row.get("day_of_week")) else None,
                hour_of_day=int(row.get("hour_of_day")) if pd.notna(row.get("hour_of_day")) else None,
                state=str(row.get("state", "")) if pd.notna(row.get("state")) else None,
                district=str(row.get("district", "")) if pd.notna(row.get("district")) else None,
                location_type=str(row.get("location_type", "")) if pd.notna(row.get("location_type")) else None,
                latitude=float(row.get("latitude")) if pd.notna(row.get("latitude")) else None,
                longitude=float(row.get("longitude")) if pd.notna(row.get("longitude")) else None,
                road_type=str(row.get("road_type", "")) if pd.notna(row.get("road_type")) else None,
                road_condition=str(row.get("road_condition", "")) if pd.notna(row.get("road_condition")) else None,
                weather=str(row.get("weather", "")) if pd.notna(row.get("weather")) else None,
                light_condition=str(row.get("light_condition", "")) if pd.notna(row.get("light_condition")) else None,
                accident_severity=str(row.get("accident_severity", "")) if pd.notna(row.get("accident_severity")) else None,
                fatalities_count=int(row.get("fatalities_count", 0)) if pd.notna(row.get("fatalities_count")) else 0,
                injured_count=int(row.get("injured_count", 0)) if pd.notna(row.get("injured_count")) else 0,
                vehicles_involved_count=int(row.get("vehicles_involved_count", 1)) if pd.notna(row.get("vehicles_involved_count")) else 1,
                collision_type=str(row.get("collision_type", "")) if pd.notna(row.get("collision_type")) else None,
                primary_vehicle_type=str(row.get("primary_vehicle_type", "")) if pd.notna(row.get("primary_vehicle_type")) else None,
                contributing_factor=str(row.get("contributing_factor", "")) if pd.notna(row.get("contributing_factor")) else None,
                data_origin=str(row.get("data_origin", "")) if pd.notna(row.get("data_origin")) else None,
            )
            records.append(record)
            if len(records) >= batch_size:
                self.db.bulk_save_objects(records)
                self.db.commit()
                records = []
        if records:
            self.db.bulk_save_objects(records)
            self.db.commit()

    # ------------------ Records Querying to DataFrame ------------------
    def get_records_df(
        self,
        dataset_id: Optional[int] = None,
        state: Optional[str] = None,
        severity: Optional[str] = None,
        year: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        weather: Optional[str] = None,
        road_type: Optional[str] = None,
        limit: Optional[int] = None
    ) -> pd.DataFrame:
        """Fetches accident records as a Pandas DataFrame for downstream analytical computation."""
        query = self.db.query(AccidentRecord)
        if dataset_id:
            query = query.filter(AccidentRecord.dataset_id == dataset_id)
        if state and state != "All":
            query = query.filter(AccidentRecord.state == state)
        if severity and severity != "All":
            query = query.filter(AccidentRecord.accident_severity == severity)
        if year and year != 0:
            query = query.filter(AccidentRecord.year == year)
        if start_date:
            query = query.filter(AccidentRecord.accident_date >= start_date)
        if end_date:
            query = query.filter(AccidentRecord.accident_date <= end_date)
        if weather and weather != "All":
            query = query.filter(AccidentRecord.weather == weather)
        if road_type and road_type != "All":
            query = query.filter(AccidentRecord.road_type == road_type)

        if limit:
            query = query.limit(limit)

        records = query.all()
        if not records:
            return pd.DataFrame()

        data = [
            {
                "id": r.id,
                "accident_id": r.accident_id,
                "accident_date": r.accident_date,
                "accident_time": r.accident_time,
                "year": r.year,
                "month": r.month,
                "day_of_week": r.day_of_week,
                "hour_of_day": r.hour_of_day,
                "state": r.state,
                "district": r.district,
                "location_type": r.location_type,
                "latitude": r.latitude,
                "longitude": r.longitude,
                "road_type": r.road_type,
                "road_condition": r.road_condition,
                "weather": r.weather,
                "light_condition": r.light_condition,
                "accident_severity": r.accident_severity,
                "fatalities_count": r.fatalities_count,
                "injured_count": r.injured_count,
                "vehicles_involved_count": r.vehicles_involved_count,
                "collision_type": r.collision_type,
                "primary_vehicle_type": r.primary_vehicle_type,
                "contributing_factor": r.contributing_factor,
                "data_origin": r.data_origin
            }
            for r in records
        ]
        return pd.DataFrame(data)

    def get_records_paginated(
        self,
        dataset_id: Optional[int] = None,
        page: int = 1,
        page_size: int = 50,
        search: Optional[str] = None,
        state: Optional[str] = None,
        severity: Optional[str] = None,
        year: Optional[int] = None
    ) -> Tuple[List[Dict[str, Any]], int]:
        query = self.db.query(AccidentRecord)
        if dataset_id:
            query = query.filter(AccidentRecord.dataset_id == dataset_id)
        if state and state != "All":
            query = query.filter(AccidentRecord.state == state)
        if severity and severity != "All":
            query = query.filter(AccidentRecord.accident_severity == severity)
        if year and year != 0:
            query = query.filter(AccidentRecord.year == year)
        if search:
            search_filter = or_(
                AccidentRecord.accident_id.ilike(f"%{search}%"),
                AccidentRecord.state.ilike(f"%{search}%"),
                AccidentRecord.district.ilike(f"%{search}%"),
                AccidentRecord.collision_type.ilike(f"%{search}%"),
                AccidentRecord.contributing_factor.ilike(f"%{search}%"),
                AccidentRecord.primary_vehicle_type.ilike(f"%{search}%"),
            )
            query = query.filter(search_filter)

        total = query.count()
        offset = (page - 1) * page_size
        records = query.order_by(desc(AccidentRecord.accident_date)).offset(offset).limit(page_size).all()
        
        result = [
            {
                "id": r.id,
                "accident_id": r.accident_id,
                "accident_date": r.accident_date,
                "year": r.year,
                "state": r.state,
                "district": r.district,
                "accident_severity": r.accident_severity,
                "fatalities_count": r.fatalities_count,
                "injured_count": r.injured_count,
                "collision_type": r.collision_type,
                "primary_vehicle_type": r.primary_vehicle_type,
                "contributing_factor": r.contributing_factor,
                "road_type": r.road_type,
                "weather": r.weather
            }
            for r in records
        ]
        return result, total

    # ------------------ Quality Reports ------------------
    def save_quality_report(
        self,
        dataset_id: int,
        total_records: int,
        missing_cells: int,
        duplicate_rows: int,
        anomaly_count: int,
        quality_score: float,
        metrics_dict: dict
    ) -> DataQualityReport:
        report = DataQualityReport(
            dataset_id=dataset_id,
            total_records=total_records,
            missing_cells=missing_cells,
            duplicate_rows=duplicate_rows,
            anomaly_count=anomaly_count,
            quality_score=quality_score,
            metrics_json=json.dumps(metrics_dict)
        )
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        return report

    def get_latest_quality_report(self, dataset_id: int) -> Optional[DataQualityReport]:
        return self.db.query(DataQualityReport).filter(DataQualityReport.dataset_id == dataset_id).order_by(desc(DataQualityReport.created_at)).first()

    # ------------------ Reports History ------------------
    def save_report_history(
        self,
        title: str,
        report_type: str,
        file_path: str,
        format: str = "pdf",
        date_range_start: Optional[str] = None,
        date_range_end: Optional[str] = None
    ) -> ReportHistory:
        report = ReportHistory(
            title=title,
            report_type=report_type,
            file_path=file_path,
            format=format,
            date_range_start=date_range_start,
            date_range_end=date_range_end,
            status="completed"
        )
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        return report

    def get_report_history(self, limit: int = 50) -> List[ReportHistory]:
        return self.db.query(ReportHistory).order_by(desc(ReportHistory.generated_at)).limit(limit).all()
