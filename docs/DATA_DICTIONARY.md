# DATA DICTIONARY & CANONICAL SCHEMA SPECIFICATION
## TRAFFIC TREND — Road Safety Intelligence & Accident Analytics Platform
*Version: 2.0.0 | Academic & Production Standard*

---

## 1. Overview

The platform uses a canonical 24-dimension road safety schema designed to seamlessly ingest and normalize diverse municipal, state, and national traffic collision records.

---

## 2. Canonical Accident Record Schema

| Field Name | Type | Nullable | Canonical Values / Format | Description & Analytical Role |
| :--- | :--- | :---: | :--- | :--- |
| `accident_id` | String | No | Unique String (e.g. `ACC-IND-2020-000001`) | Unique identifier for the crash event. Primary key in analytics deduplication. |
| `accident_date` | Date/String | No | `YYYY-MM-DD` (ISO 8601) | Calendar date of occurrence. Foundation for time-series forecasting and moving averages. |
| `accident_time` | Time/String | Yes | `HH:MM:SS` (24-hour clock) | Time of incident. Drives diurnal 24-hour distribution and peak rush hour detection. |
| `year` | Integer | Yes | `2018` – `2026` | Calendar year of incident. Enables longitudinal Year-over-Year (YoY%) growth tracking. |
| `month` | String | Yes | `January` – `December` | Calendar month. Drives cyclical seasonality distributions. |
| `day_of_week` | String | Yes | `Monday` – `Sunday` | Day of week. Distinguishes weekday commute collisions from weekend recreational crashes. |
| `hour_of_day` | Integer | Yes | `0` – `23` | Integer hour (0-23). Used for bivariate day-hour collision density heatmaps. |
| `state` | String | Yes | Proper Name (e.g. `Maharashtra`, `Tamil Nadu`) | Primary administrative regional jurisdiction. Used for state risk rankings. |
| `district` | String | Yes | Proper Name (e.g. `Mumbai`, `Coimbatore`) | Secondary administrative area. Enables localized density and hotspot auditing. |
| `location_type` | String | Yes | `Urban`, `Rural`, `Semi-Urban` | Locality classification for urban arterial vs rural highway contrast. |
| `latitude` | Float | Yes | $[-90.0, 90.0]$ | WGS84 GPS latitude for spatial MapLibre GL mapping. |
| `longitude` | Float | Yes | $[-180.0, 180.0]$ | WGS84 GPS longitude for spatial MapLibre GL mapping. |
| `road_type` | String | Yes | `Expressway`, `National Highway`, `State Highway`, `Urban Arterial`, `Local Road` | Roadway engineering class. Analyzes highway vs municipal crash vulnerability. |
| `road_condition`| String | Yes | `Dry & Clear`, `Wet & Slippery`, `Under Construction`, `Potholed` | Surface physical state. Correlates infrastructural hazards with impact. |
| `weather` | String | Yes | `Clear / Sunny`, `Rain / Monsoon`, `Fog / Smog`, `Overcast / Cloudy` | Atmospheric condition at time of collision. |
| `light_condition`| String| Yes | `Daylight`, `Dark - Street Lights Lit`, `Dark - Unlighted`, `Dusk / Dawn` | Ambient illumination level. |
| `accident_severity`| String| No | `Fatal`, `Grievous Injury`, `Minor Injury`, `Property Damage Only` | Categorical impact severity. Determines lethal vs non-lethal casualty proportions. |
| `fatalities_count`| Integer| No | $\ge 0$ | Number of deceased individuals. Key numerator for fatality rates. |
| `injured_count` | Integer| No | $\ge 0$ | Number of injured persons. Key numerator for casualty rates. |
| `vehicles_involved_count`| Integer| Yes | $\ge 1$ | Total vehicles involved in crash impact. |
| `collision_type`| String | Yes | `Head-on Collision`, `Rear-end Collision`, `Side-swipe / T-Bone`, `Hit-pedestrian`, `Rollover` | Mechanical manner of crash impact. |
| `primary_vehicle_type`| String| Yes | `Two-Wheeler`, `Car / Private SUV`, `Heavy Commercial Truck`, `Bus`, `Auto-Rickshaw`, `Bicycle`, `Pedestrian` | Primary offending or most impacted vehicle class. |
| `contributing_factor`| String| Yes | `Overspeeding Above Limit`, `Distracted Driving`, `Drunk Driving / DUI`, `Lane Violation`, `Mechanical Failure`, `Weather` | Identified human behavioral or mechanical trigger. |
| `data_origin` | String | Yes | String metadata | Provenance tag distinguishing real police telemetry from demonstration benchmarks. |

---

## 3. Intelligent Synonym Mapping Dictionary

When arbitrary user CSV or Excel files are ingested, the platform dynamically matches column names using normalized snake_case string distance:

- **Accident Identifier:** `accident_id`, `crash_id`, `incident_id`, `case_id`, `collision_id`, `id`, `record_id`
- **Date:** `accident_date`, `crash_date`, `incident_date`, `date`, `collision_date`, `date_time`
- **Time:** `accident_time`, `crash_time`, `incident_time`, `time`, `time_of_day`
- **State:** `state`, `province`, `state_name`, `region`, `jurisdiction`, `admin_state`
- **District:** `district`, `county`, `district_name`, `city`, `borough`, `police_station`, `area`
- **Coordinates:** `latitude` (`lat`, `y_coord`), `longitude` (`long`, `lon`, `x_coord`)
- **Severity:** `accident_severity`, `severity`, `crash_severity`, `injury_severity`, `level`
- **Fatalities:** `fatalities_count`, `fatalities`, `persons_killed`, `killed`, `deaths`, `number_of_fatalities`
- **Injuries:** `injured_count`, `injured`, `persons_injured`, `injuries`, `casualty_count`
- **Vehicles:** `primary_vehicle_type`, `vehicle_type`, `offending_vehicle`, `vehicle`
- **Contributing Factor:** `contributing_factor`, `cause`, `accident_cause`, `reason`, `violation`
