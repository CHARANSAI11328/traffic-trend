"""
Application Configuration and Theme Constants
TRAFFIC TREND — Road Accident Data Analysis & Intelligence Platform
"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List
import os

# Project Root Directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
EXPORTS_DIR = DATA_DIR / "exports"
DATABASE_DIR = DATA_DIR / "database"
LOGS_DIR = BASE_DIR / "logs"

# Ensure runtime directories exist
for path in [RAW_DATA_DIR, PROCESSED_DATA_DIR, EXPORTS_DIR, DATABASE_DIR, LOGS_DIR]:
    path.mkdir(parents=True, exist_ok=True)

# Database URI
DEFAULT_DB_PATH = DATABASE_DIR / "traffic_trend.db"
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_DB_PATH.as_posix()}")

# Logging Configuration
LOG_FILE_PATH = LOGS_DIR / "traffic_trend.log"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Color Palette: Deep Navy / Charcoal with Cyan, Blue, Emerald, Amber, Crimson
class Palette:
    BG_DARK = "#0d1117"
    BG_CARD = "#161b22"
    BG_CARD_HOVER = "#1f242c"
    BORDER = "#30363d"
    TEXT_MAIN = "#f0f6fc"
    TEXT_MUTED = "#8b949e"
    ACCENT_CYAN = "#38bdf8"
    ACCENT_BLUE = "#2563eb"
    ACCENT_INDIGO = "#6366f1"
    
    # Severity & Status Colors
    FATAL_RED = "#ef4444"
    GRIEVOUS_ORANGE = "#f97316"
    MINOR_YELLOW = "#eab308"
    SAFE_GREEN = "#10b981"
    INFO_BLUE = "#3b82f6"

    # Chart Palette
    CHART_COLORS: List[str] = [
        "#38bdf8", "#818cf8", "#34d399", "#fbbf24",
        "#f87171", "#a78bfa", "#f472b6", "#2dd4bf"
    ]


@dataclass
class AppConfig:
    APP_NAME: str = "TRAFFIC TREND"
    APP_SUBTITLE: str = "Road Safety Intelligence & Accident Analytics"
    VERSION: str = "2.4.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "Production")
    MAX_UPLOAD_SIZE_MB: int = 200
    BENCHMARK_DEMO_FILENAME: str = "traffic_accidents_benchmark_demonstration.csv"
    BENCHMARK_DEMO_PATH: Path = RAW_DATA_DIR / "traffic_accidents_benchmark_demonstration.csv"
    BENCHMARK_DEMO_EXCEL: Path = RAW_DATA_DIR / "traffic_accidents_benchmark_demonstration.xlsx"
    CANONICAL_COLUMNS: List[str] = field(default_factory=lambda: [
        "accident_id", "accident_date", "accident_time", "year", "month",
        "day_of_week", "hour_of_day", "state", "district", "location_type",
        "latitude", "longitude", "road_type", "road_condition", "weather",
        "light_condition", "accident_severity", "fatalities_count",
        "injured_count", "vehicles_involved_count", "collision_type",
        "primary_vehicle_type", "contributing_factor"
    ])


CONFIG = AppConfig()

