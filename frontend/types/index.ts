export interface KPISnapshot {
  total_accidents: number;
  total_fatalities: number;
  total_injured: number;
  total_casualties: number;
  fatal_accidents_count: number;
  non_fatal_accidents_count: number;
  fatality_rate_pct: number;
  casualty_rate_per_crash: number;
  avg_accidents_per_day: number;
  most_affected_region: string;
  most_affected_time_window: string;
  fatal_accidents_ratio_pct: number;
  data_coverage_period: string;
  accidents_delta_pct?: number | null;
  fatalities_delta_pct?: number | null;
  injured_delta_pct?: number | null;
}

export interface FilterOptions {
  states: string[];
  severities: string[];
  years: number[];
  weather: string[];
  road_types: string[];
}

export interface OverviewData {
  kpis: KPISnapshot;
  yearly_trend: any[];
  top_states: any[];
  severity_breakdown: any[];
  recent_observations: string[];
  filter_options: FilterOptions;
}

export interface TrendData {
  yearly: any[];
  monthly: any[];
  day_of_week: any[];
  hourly: any[];
  day_hour_heatmap: any[];
}

export interface GeographyData {
  states: any[];
  districts: any[];
  map_points: any[];
  hotspots: any[];
}

export interface SeverityData {
  distribution: any[];
  by_vehicle: any[];
  by_road_type: any[];
  by_weather: any[];
}

export interface AccidentRecord {
  id: number;
  accident_id: string;
  accident_date: string;
  year?: number;
  state?: string;
  district?: string;
  accident_severity?: string;
  fatalities_count: number;
  injured_count: number;
  collision_type?: string;
  primary_vehicle_type?: string;
  contributing_factor?: string;
  road_type?: string;
  weather?: string;
}

export interface PaginatedAccidents {
  records: AccidentRecord[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface DatasetItem {
  id: number;
  name: string;
  filename: string;
  row_count: number;
  column_count: number;
  upload_date: string;
  status: string;
  is_active: boolean;
  origin?: string;
  description?: string;
}

export interface QualityProfile {
  dataset_id: number;
  total_records: number;
  total_columns: number;
  completeness_score: number;
  uniqueness_score: number;
  validity_score: number;
  consistency_score: number;
  overall_score: number;
  quality_grade: string;
  duplicate_count: number;
  duplicate_pct: number;
  total_missing_cells: number;
  missing_cells_pct: number;
  invalid_dates_count: number;
  invalid_coords_count: number;
  column_profiles: Record<string, any>;
  scoring_methodology: Record<string, string>;
}

export interface SystemStatus {
  status: string;
  environment: string;
  version: string;
  database: {
    type: string;
    status: string;
    latency_ms: number;
  };
  storage: {
    free_disk_gb: number;
    total_disk_gb: number;
  };
  timestamp: number;
}

export interface DataFreshness {
  active_dataset_id?: number;
  active_dataset_name: string;
  feed_mode: string;
  live_feed_connected: boolean;
  data_origin: string;
  earliest_incident_date: string;
  latest_incident_date: string;
  total_records: number;
  last_ingestion_timestamp: string;
  freshness_status: string;
  disclaimer: string;
}

export interface FilterState {
  state: string;
  severity: string;
  year: number;
  weather: string;
  road_type: string;
  start_date?: string;
  end_date?: string;
}
