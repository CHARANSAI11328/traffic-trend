from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, Query
from backend.app.api.dependencies import get_repo
from backend.app.database.repository import DatabaseRepository
from backend.app.analytics.anomalies import AnomalyDetector
from backend.app.analytics.forecasting import ForecastingEngine
from backend.app.analytics.correlation import CorrelationAnalyzer
from backend.app.analytics.geography import GeographicalAnalyzer

router = APIRouter()

@router.get("/accidents")
def get_accidents_table(
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=5, le=100),
    search: Optional[str] = Query(None),
    state: Optional[str] = Query("All"),
    severity: Optional[str] = Query("All"),
    year: Optional[int] = Query(0),
    repo: DatabaseRepository = Depends(get_repo)
):
    active_dataset = repo.get_active_dataset()
    dataset_id = active_dataset.id if active_dataset else None

    records, total = repo.get_records_paginated(
        dataset_id=dataset_id,
        page=page,
        page_size=page_size,
        search=search,
        state=state,
        severity=severity,
        year=year
    )

    total_pages = (total + page_size - 1) // page_size if total > 0 else 1

    return {
        "records": records,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages
    }

@router.get("/regions")
def get_regional_risk_rankings(
    state: Optional[str] = Query("All"),
    year: Optional[int] = Query(0),
    repo: DatabaseRepository = Depends(get_repo)
):
    active_dataset = repo.get_active_dataset()
    dataset_id = active_dataset.id if active_dataset else None

    df = repo.get_records_df(dataset_id=dataset_id, state=state, year=year)
    states = GeographicalAnalyzer.analyze_by_state(df)
    districts = GeographicalAnalyzer.analyze_by_district(df, state_filter=state, limit=30)

    return {
        "states": states,
        "districts": districts
    }

@router.get("/anomalies")
def get_statistical_anomalies(
    repo: DatabaseRepository = Depends(get_repo)
):
    active_dataset = repo.get_active_dataset()
    dataset_id = active_dataset.id if active_dataset else None

    df = repo.get_records_df(dataset_id=dataset_id)
    regional_spikes = AnomalyDetector.detect_regional_spikes(df)
    fatality_spikes = AnomalyDetector.detect_fatality_spikes(df)

    return {
        "regional_spikes": regional_spikes,
        "fatality_spikes": fatality_spikes,
        "total_anomalies": len(regional_spikes) + len(fatality_spikes),
        "methodology": "Z-score anomaly detection (|Z| > 1.96) combined with Tukey Interquartile Range fence (Q3 + 1.5 * IQR)."
    }

@router.get("/forecast")
def get_accident_forecast(
    horizon: int = Query(6, ge=1, le=24),
    repo: DatabaseRepository = Depends(get_repo)
):
    active_dataset = repo.get_active_dataset()
    dataset_id = active_dataset.id if active_dataset else None

    df = repo.get_records_df(dataset_id=dataset_id)
    forecast = ForecastingEngine.generate_forecast(df, horizon_periods=horizon)
    return forecast

@router.get("/correlation")
def get_correlation_matrix(
    repo: DatabaseRepository = Depends(get_repo)
):
    active_dataset = repo.get_active_dataset()
    dataset_id = active_dataset.id if active_dataset else None

    df = repo.get_records_df(dataset_id=dataset_id)
    return CorrelationAnalyzer.compute_correlation_matrix(df)
