from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel

class DatasetResponse(BaseModel):
    id: int
    name: str
    filename: str
    row_count: int
    column_count: int
    upload_date: datetime
    status: str
    is_active: bool
    origin: Optional[str] = None
    description: Optional[str] = None

    class Config:
        from_attributes = True

class UploadResponse(BaseModel):
    dataset_id: int
    filename: str
    row_count: int
    column_count: int
    detected_mappings: Dict[str, str]
    message: str

class ProfileResponse(BaseModel):
    dataset_id: int
    total_records: int
    total_columns: int
    completeness_score: float
    uniqueness_score: float
    validity_score: float
    consistency_score: float
    overall_score: float
    quality_grade: str
    duplicate_count: int
    duplicate_pct: float
    total_missing_cells: int
    missing_cells_pct: float
    invalid_dates_count: int
    invalid_coords_count: int
    column_profiles: Dict[str, Dict[str, Any]]
    scoring_methodology: Dict[str, str]

class CleaningOptionsSchema(BaseModel):
    drop_duplicates: bool = True
    handle_missing_dates: str = "drop"
    handle_missing_severity: str = "impute_unknown"
    handle_missing_casualties: str = "impute_zero"
    impute_missing_categoricals: bool = True
    categorical_fill_value: str = "Unknown"
    validate_coordinates: bool = True
    enforce_non_negative_casualties: bool = True

class CleanSummarySchema(BaseModel):
    original_records: int
    retained_records: int
    duplicates_removed: int
    missing_imputed_count: int
    invalid_dates_dropped: int
    invalid_coordinates_nulled: int
    negative_casualties_corrected: int
    final_records: int
    modifications_log: List[str]
