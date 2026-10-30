from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, Query
from backend.app.api.dependencies import get_repo
from backend.app.database.repository import DatabaseRepository
from backend.app.analytics.kpis import KPICalculator, KPISnapshot
from backend.app.analytics.trends import TrendAnalyzer
from backend.app.analytics.geography import GeographicalAnalyzer
from backend.app.analytics.severity import SeverityAnalyzer
from backend.app.schemas.dashboard import (
    OverviewResponse, TrendResponse, GeographyResponse, SeverityResponse, KPISchema
)

router = APIRouter()

@router.get("/overview", response_model=OverviewResponse)
def get_dashboard_overview(
    state: Optional[str] = Query("All"),
    severity: Optional[str] = Query("All"),
    year: Optional[int] = Query(0),
    weather: Optional[str] = Query("All"),
    road_type: Optional[str] = Query("All"),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    repo: DatabaseRepository = Depends(get_repo)
):
    active_dataset = repo.get_active_dataset()
    dataset_id = active_dataset.id if active_dataset else None

    # Fetch filtered DataFrame
    df = repo.get_records_df(
        dataset_id=dataset_id,
        state=state,
        severity=severity,
        year=year,
        start_date=start_date,
        end_date=end_date,
        weather=weather,
        road_type=road_type
    )

    # Compute comparison period (prior year if single year selected, or prior half)
    prior_df = None
    if year and year > 0:
        prior_df = repo.get_records_df(
            dataset_id=dataset_id,
            state=state,
            severity=severity,
            year=year - 1,
            weather=weather,
            road_type=road_type
        )

    # Dynamic KPI calculation
    kpis = KPICalculator.compute(df, prior_df=prior_df)
    
    # Trends
    yearly = TrendAnalyzer.analyze_yearly_trend(df)
    
    # Geography
    states = GeographicalAnalyzer.analyze_by_state(df)[:8]
    
    # Severity breakdown
    severity_breakdown = SeverityAnalyzer.analyze_severity_distribution(df)

    # Generate analytical observations dynamically
    observations = []
    if kpis.total_accidents > 0:
        observations.append(f"Recorded volume includes {kpis.total_accidents:,} crash events resulting in {kpis.total_fatalities:,} fatalities ({kpis.fatality_rate_pct:.1f}% fatality rate).")
        observations.append(f"Highest geographic density observed in {kpis.most_affected_region}.")
        observations.append(f"Diurnal crash frequency peaks within the {kpis.most_affected_time_window} interval.")
        if kpis.fatal_accidents_count > 0:
            observations.append(f"Fatal collisions represent {kpis.fatal_accidents_ratio_pct:.1f}% of all incidents.")
    else:
        observations.append("No recorded accident records match the selected filter criteria.")

    # Filter options from all records
    full_df = repo.get_records_df(dataset_id=dataset_id, limit=3500)
    filter_options = {
        "states": sorted(list(full_df["state"].dropna().unique())) if "state" in full_df.columns else [],
        "severities": sorted(list(full_df["accident_severity"].dropna().unique())) if "accident_severity" in full_df.columns else [],
        "years": sorted([int(y) for y in full_df["year"].dropna().unique() if y > 0]) if "year" in full_df.columns else [],
        "weather": sorted(list(full_df["weather"].dropna().unique())) if "weather" in full_df.columns else [],
        "road_types": sorted(list(full_df["road_type"].dropna().unique())) if "road_type" in full_df.columns else []
    }

    return OverviewResponse(
        kpis=KPISchema(**kpis.__dict__),
        yearly_trend=yearly,
        top_states=states,
        severity_breakdown=severity_breakdown,
        recent_observations=observations,
        filter_options=filter_options
    )

@router.get("/trends", response_model=TrendResponse)
def get_dashboard_trends(
    state: Optional[str] = Query("All"),
    severity: Optional[str] = Query("All"),
    year: Optional[int] = Query(0),
    repo: DatabaseRepository = Depends(get_repo)
):
    active_dataset = repo.get_active_dataset()
    dataset_id = active_dataset.id if active_dataset else None

    df = repo.get_records_df(dataset_id=dataset_id, state=state, severity=severity, year=year)

    yearly = TrendAnalyzer.analyze_yearly_trend(df)
    monthly = TrendAnalyzer.analyze_monthly_trend(df)
    day_of_week = TrendAnalyzer.analyze_day_of_week(df)
    hourly = TrendAnalyzer.analyze_hourly_distribution(df)
    day_hour_heatmap = TrendAnalyzer.analyze_day_hour_heatmap(df)

    return TrendResponse(
        yearly=yearly,
        monthly=monthly,
        day_of_week=day_of_week,
        hourly=hourly,
        day_hour_heatmap=day_hour_heatmap
    )

@router.get("/geography", response_model=GeographyResponse)
def get_dashboard_geography(
    state: Optional[str] = Query("All"),
    severity: Optional[str] = Query("All"),
    year: Optional[int] = Query(0),
    repo: DatabaseRepository = Depends(get_repo)
):
    active_dataset = repo.get_active_dataset()
    dataset_id = active_dataset.id if active_dataset else None

    df = repo.get_records_df(dataset_id=dataset_id, state=state, severity=severity, year=year)

    states = GeographicalAnalyzer.analyze_by_state(df)
    districts = GeographicalAnalyzer.analyze_by_district(df, state_filter=state, limit=25)
    map_points = GeographicalAnalyzer.get_map_points(df, limit=1200)
    hotspots = GeographicalAnalyzer.detect_hotspots(df, top_n=10)

    return GeographyResponse(
        states=states,
        districts=districts,
        map_points=map_points,
        hotspots=hotspots
    )

@router.get("/severity", response_model=SeverityResponse)
def get_dashboard_severity(
    state: Optional[str] = Query("All"),
    year: Optional[int] = Query(0),
    repo: DatabaseRepository = Depends(get_repo)
):
    active_dataset = repo.get_active_dataset()
    dataset_id = active_dataset.id if active_dataset else None

    df = repo.get_records_df(dataset_id=dataset_id, state=state, year=year)

    distribution = SeverityAnalyzer.analyze_severity_distribution(df)
    by_vehicle = SeverityAnalyzer.analyze_by_vehicle_type(df)
    by_road_type = SeverityAnalyzer.analyze_by_road_type(df)
    by_weather = SeverityAnalyzer.analyze_by_weather(df)

    return SeverityResponse(
        distribution=distribution,
        by_vehicle=by_vehicle,
        by_road_type=by_road_type,
        by_weather=by_weather
    )
