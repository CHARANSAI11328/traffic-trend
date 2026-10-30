import shutil
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from backend.app.api.dependencies import get_repo, require_admin
from backend.app.database.repository import DatabaseRepository
from backend.app.core.config import settings
from backend.app.data.loader import DataLoader
from backend.app.data.cleaner import DataCleaner, CleaningOptions
from backend.app.data.profiler import DataProfiler
from backend.app.schemas.dataset import (
    DatasetResponse, UploadResponse, ProfileResponse, CleaningOptionsSchema, CleanSummarySchema
)

router = APIRouter()

@router.get("", response_model=List[DatasetResponse])
def list_datasets(repo: DatabaseRepository = Depends(get_repo)):
    return repo.get_datasets()

@router.post("/upload", response_model=UploadResponse)
async def upload_dataset(
    file: UploadFile = File(...),
    description: Optional[str] = Form(None),
    repo: DatabaseRepository = Depends(get_repo),
    _admin = Depends(require_admin)
):
    ext = Path(file.filename).suffix.lower()
    if ext not in DataLoader.SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type '{ext}'. Allowed: {DataLoader.SUPPORTED_EXTENSIONS}"
        )

    # Save to raw storage
    dest_path = settings.RAW_DATA_DIR / file.filename
    with open(dest_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        df, meta = DataLoader.load_file(dest_path)
    except Exception as e:
        if dest_path.exists():
            dest_path.unlink()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to parse file: {str(e)}")

    dataset = repo.create_dataset(
        name=Path(file.filename).stem.replace("_", " ").title(),
        filename=file.filename,
        file_path=str(dest_path),
        row_count=meta["record_count"],
        column_count=meta["column_count"],
        origin="Manual Upload",
        description=description,
        is_active=False
    )

    repo.log("INFO", f"Uploaded dataset '{file.filename}' with {meta['record_count']} rows", "DatasetManager")

    return UploadResponse(
        dataset_id=dataset.id,
        filename=file.filename,
        row_count=meta["record_count"],
        column_count=meta["column_count"],
        detected_mappings=meta["detected_mappings"],
        message="Dataset uploaded successfully. Ready for profiling and cleaning."
    )

@router.get("/{dataset_id}", response_model=DatasetResponse)
def get_dataset(dataset_id: int, repo: DatabaseRepository = Depends(get_repo)):
    ds = repo.get_dataset_by_id(dataset_id)
    if not ds:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")
    return ds

@router.delete("/{dataset_id}")
def delete_dataset(dataset_id: int, repo: DatabaseRepository = Depends(get_repo), _admin = Depends(require_admin)):
    ds = repo.get_dataset_by_id(dataset_id)
    if not ds:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")
    
    success = repo.delete_dataset(dataset_id)
    if success:
        repo.log("INFO", f"Deleted dataset ID {dataset_id}", "DatasetManager")
        return {"message": "Dataset deleted successfully"}
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to delete dataset")

@router.post("/{dataset_id}/activate")
def activate_dataset(dataset_id: int, repo: DatabaseRepository = Depends(get_repo), _admin = Depends(require_admin)):
    ds = repo.set_active_dataset(dataset_id)
    if not ds:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")
    repo.log("INFO", f"Activated dataset ID {dataset_id} ('{ds.name}')", "DatasetManager")
    return {"message": f"Dataset '{ds.name}' is now active for analytics"}

@router.post("/{dataset_id}/profile", response_model=ProfileResponse)
def profile_dataset(dataset_id: int, repo: DatabaseRepository = Depends(get_repo)):
    ds = repo.get_dataset_by_id(dataset_id)
    if not ds:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")

    file_path = Path(ds.file_path)
    if not file_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Physical dataset file missing on server")

    df, _ = DataLoader.load_file(file_path)
    scorecard = DataProfiler.profile(df)

    # Persist report to DB
    repo.save_quality_report(
        dataset_id=dataset_id,
        total_records=scorecard.total_records,
        missing_cells=scorecard.total_missing_cells,
        duplicate_rows=scorecard.duplicate_count,
        anomaly_count=scorecard.invalid_dates_count + scorecard.invalid_coords_count,
        quality_score=scorecard.overall_score,
        metrics_dict=scorecard.__dict__
    )

    repo.log("INFO", f"Profiled dataset ID {dataset_id}: Quality Score {scorecard.overall_score}/100", "DataProfiler")

    return ProfileResponse(
        dataset_id=dataset_id,
        **scorecard.__dict__
    )

@router.post("/{dataset_id}/clean")
def clean_dataset(
    dataset_id: int,
    options: CleaningOptionsSchema,
    apply_to_db: bool = False,
    repo: DatabaseRepository = Depends(get_repo),
    _admin = Depends(require_admin)
):
    ds = repo.get_dataset_by_id(dataset_id)
    if not ds:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")

    file_path = Path(ds.file_path)
    if not file_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Physical dataset file missing on server")

    df, _ = DataLoader.load_file(file_path)
    clean_opts = CleaningOptions(
        drop_duplicates=options.drop_duplicates,
        handle_missing_dates=options.handle_missing_dates,
        handle_missing_severity=options.handle_missing_severity,
        handle_missing_casualties=options.handle_missing_casualties,
        impute_missing_categoricals=options.impute_missing_categoricals,
        categorical_fill_value=options.categorical_fill_value,
        validate_coordinates=options.validate_coordinates,
        enforce_non_negative_casualties=options.enforce_non_negative_casualties
    )

    cleaned_df, summary = DataCleaner.clean(df, clean_opts)

    if apply_to_db:
        # Save cleaned file into processed directory
        clean_filename = f"cleaned_{Path(ds.filename).stem}.parquet"
        clean_path = settings.PROCESSED_DATA_DIR / clean_filename
        cleaned_df.to_parquet(clean_path, index=False)

        # Ingest into database
        repo.bulk_insert_records(dataset_id=dataset_id, df=cleaned_df)
        ds.row_count = len(cleaned_df)
        ds.file_path = str(clean_path)
        ds.status = "ready"
        repo.db.commit()
        repo.set_active_dataset(dataset_id)

        repo.log("INFO", f"Cleaned & ingested dataset ID {dataset_id} ({len(cleaned_df)} records)", "DataCleaner")

    return {
        "dataset_id": dataset_id,
        "applied_to_db": apply_to_db,
        "summary": summary.__dict__,
        "sample_preview": cleaned_df.head(5).to_dict(orient="records")
    }
