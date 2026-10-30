import os
from pathlib import Path
from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Base directory for the repository
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"

class Settings(BaseSettings):
    PROJECT_NAME: str = "TRAFFIC TREND - Road Safety Intelligence & Accident Analytics"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    
    # Database
    DATABASE_URL: str = "sqlite:///./data/database/traffic_trend.db"
    
    # Security
    SECRET_KEY: str = "traffictrend-secure-secret-key-2026-road-safety-platform"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Initial Admin Seed
    ADMIN_DEFAULT_EMAIL: str = "admin@traffictrend.io"
    ADMIN_DEFAULT_PASSWORD: str = "TrafficTrend2026!"
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ]
    
    @field_validator("CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    # Directories
    RAW_DATA_DIR: Path = DATA_DIR / "raw"
    PROCESSED_DATA_DIR: Path = DATA_DIR / "processed"
    EXPORTS_DATA_DIR: Path = DATA_DIR / "exports"
    DATABASE_DIR: Path = DATA_DIR / "database"

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

# Ensure directories exist
for path in [settings.RAW_DATA_DIR, settings.PROCESSED_DATA_DIR, settings.EXPORTS_DATA_DIR, settings.DATABASE_DIR]:
    path.mkdir(parents=True, exist_ok=True)
