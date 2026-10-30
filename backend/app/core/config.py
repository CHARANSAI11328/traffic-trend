import os
from pathlib import Path
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
DATA_DIR = BASE_DIR / "data"

class Settings(BaseSettings):
    PROJECT_NAME: str = "TRAFFIC TREND - Road Safety Intelligence & Accident Analytics"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "traffictrend-secure-secret-key-2026-road-safety-platform"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{DATA_DIR / 'database' / 'traffic_trend.db'}"
    )
    
    # Default Admin
    ADMIN_DEFAULT_EMAIL: str = os.getenv("ADMIN_DEFAULT_EMAIL", "admin@traffictrend.io")
    ADMIN_DEFAULT_PASSWORD: str = os.getenv("ADMIN_DEFAULT_PASSWORD", "TrafficTrend2026!")
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # CORS
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "https://traffic-trend.vercel.app"
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            if isinstance(v, str):
                import json
                try:
                    return json.loads(v)
                except Exception:
                    return [v]
            return v
        raise ValueError(v)
    
    # Directories
    RAW_DATA_DIR: Path = DATA_DIR / "raw"
    PROCESSED_DATA_DIR: Path = Path("/tmp") if os.getenv("VERCEL") else (DATA_DIR / "processed")
    EXPORTS_DATA_DIR: Path = Path("/tmp") if os.getenv("VERCEL") else (DATA_DIR / "exports")
    DATABASE_DIR: Path = Path("/tmp") if os.getenv("VERCEL") else (DATA_DIR / "database")

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

# Ensure directories exist safely (handling read-only serverless filesystems)
for path in [settings.RAW_DATA_DIR, settings.PROCESSED_DATA_DIR, settings.EXPORTS_DATA_DIR, settings.DATABASE_DIR]:
    try:
        path.mkdir(parents=True, exist_ok=True)
    except OSError:
        pass
