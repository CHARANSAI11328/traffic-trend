# DATA DICTIONARY — TRAFFIC TREND PLATFORM
**Canonical Schema & Attribute Reference Guide**

The platform operates on a **Universal Canonical Schema Architecture**. Uploaded datasets from disparate jurisdictions (e.g. Indian MoRTH, US NHTSA/FARS, UK DfT STATS19, or local traffic police departments) are dynamically mapped to the canonical dimensions detailed below.

---

## 1. Core Identification & Temporal Dimensions

| Canonical Column | Data Type | Nullable | Example Values | Description & Transformation Logic |
| :--- | :--- | :---: | :--- | :--- |
| `accident_id` | String | No | `ACC-IND-2023-000142` | Unique institutional primary identifier for the crash incident. |
| `accident_date` | Date (ISO 8601) | No | `2023-04-12` | Calendar date of occurrence. Parsed to standard `YYYY-MM-DD`. |
| `accident_time` | String | Yes | `18:45:00` | Recorded 24-hour time of crash occurrence (`HH:MM:SS`). |
| `year` | Integer | No | `2023` | Four-digit calendar year; extracted from `accident_date` if not provided. |
| `month` | String | No | `April` | Full English month name; derived from `accident_date`. |
| `day_of_week` | String | No | `Wednesday` | Day of the week; derived from `accident_date`. |
| `hour_of_day` | Integer | Yes | `18` | Integer hour block ($0$ to $23$); extracted from `accident_time`. |
| `time_window` | String (Enriched) | Yes | `Evening Rush (17:00 - 21:00)` | Diurnal operational bucket: Morning Rush, Midday, Evening Rush, Night. |
| `is_weekend` | Boolean (Enriched)| No | `False` | `True` if `day_of_week` is Saturday or Sunday; `False` otherwise. |

---

## 2. Spatial & Environmental Dimensions

| Canonical Column | Data Type | Nullable | Example Values | Description & Transformation Logic |
| :--- | :--- | :---: | :--- | :--- |
| `state` | String | No | `Maharashtra`, `Tamil Nadu` | Primary first-order administrative division (State / Province). |
| `district` | String | Yes | `Pune`, `Chennai`, `Bengaluru` | Second-order administrative division (District, County, Metro City). |
| `location_type` | String | Yes | `Urban`, `Rural` | Urban vs rural area classification. |
| `latitude` | Float | Yes | `18.5204` | WGS84 GPS Latitude in decimal degrees ($[-90.0, +90.0]$). |
| `longitude` | Float | Yes | `73.8567` | WGS84 GPS Longitude in decimal degrees ($[-180.0, +180.0]$). |
| `road_type` | String | Yes | `National Highway`, `Expressway` | Road hierarchy class (National Highway, State Highway, Expressway, Urban Arterial). |
| `road_condition` | String | Yes | `Dry & Clear`, `Wet & Slippery` | Surface condition at time of crash. |
| `weather` | String | Yes | `Clear / Sunny`, `Rainy / Monsoonal` | Atmospheric weather state at time of crash. |
| `light_condition`| String | Yes | `Daylight`, `Dark - Street Lights Lit`| Ambient lighting condition at the crash site. |

---

## 3. Severity, Casualty & Impact Dimensions

| Canonical Column | Data Type | Nullable | Example Values | Description & Transformation Logic |
| :--- | :--- | :---: | :--- | :--- |
| `accident_severity`| String | No | `Fatal`, `Grievous Injury`, `Minor Injury` | Categorical crash severity classification based on worst outcome. |
| `fatalities_count` | Integer | No | `1`, `0` | Number of persons killed within 30 days of crash. Clamped to $\ge 0$. |
| `injured_count` | Integer | No | `2`, `0` | Number of persons sustaining grievous or minor bodily injuries. |
| `total_casualties` | Integer (Enriched) | No | `3` | Sum of fatalities and injured persons ($Fatalities + Injuries$). |
| `vehicles_involved_count` | Integer | Yes | `2` | Number of motorized and non-motorized vehicles involved. |
| `casualty_severity_index` | Float (Enriched) | No | `7.0` | Weighted transport severity index: $(Fatalities \times 5) + (Injuries \times 1)$. |
| `collision_type` | String | Yes | `Head-on Collision`, `Rear-end` | Physical manner of impact between vehicles or objects. |
| `primary_vehicle_type` | String | Yes | `Two-Wheeler`, `Heavy Commercial Truck` | Predominant or offending vehicle category involved. |
| `contributing_factor` | String | Yes | `Overspeeding Above Limit`, `DUI` | Primary recorded human violation or physical trigger. |
| `data_origin` | String | No | `BENCHMARK DEMONSTRATION` | Explicit lineage flag marking source provenance. |

