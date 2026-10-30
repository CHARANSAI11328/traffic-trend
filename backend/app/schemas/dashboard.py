from typing import Optional, List, Dict, Any
from pydantic import BaseModel

class FilterParams(BaseModel):
    state: Optional[str] = "All"
    severity: Optional[str] = "All"
    year: Optional[int] = 0
    weather: Optional[str] = "All"
    road_type: Optional[str] = "All"
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class KPISchema(BaseModel):
    total_accidents: int
    total_fatalities: int
    total_injured: int
    total_casualties: int
    fatal_accidents_count: int
    non_fatal_accidents_count: int
    fatality_rate_pct: float
    casualty_rate_per_crash: float
    avg_accidents_per_day: float
    most_affected_region: str
    most_affected_time_window: str
    fatal_accidents_ratio_pct: float
    data_coverage_period: str
    accidents_delta_pct: Optional[float] = None
    fatalities_delta_pct: Optional[float] = None
    injured_delta_pct: Optional[float] = None

class OverviewResponse(BaseModel):
    kpis: KPISchema
    yearly_trend: List[Dict[str, Any]]
    top_states: List[Dict[str, Any]]
    severity_breakdown: List[Dict[str, Any]]
    recent_observations: List[str]
    filter_options: Dict[str, List[Any]]

class TrendResponse(BaseModel):
    yearly: List[Dict[str, Any]]
    monthly: List[Dict[str, Any]]
    day_of_week: List[Dict[str, Any]]
    hourly: List[Dict[str, Any]]
    day_hour_heatmap: List[Dict[str, Any]]

class GeographyResponse(BaseModel):
    states: List[Dict[str, Any]]
    districts: List[Dict[str, Any]]
    map_points: List[Dict[str, Any]]
    hotspots: List[Dict[str, Any]]

class SeverityResponse(BaseModel):
    distribution: List[Dict[str, Any]]
    by_vehicle: List[Dict[str, Any]]
    by_road_type: List[Dict[str, Any]]
    by_weather: List[Dict[str, Any]]
