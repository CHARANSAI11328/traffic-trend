import os
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.core.config import settings, BASE_DIR
from backend.app.core.security import get_password_hash
from backend.app.database.connection import engine, Base, SessionLocal
from backend.app.database.repository import DatabaseRepository
from backend.app.data.loader import DataLoader
from backend.app.data.cleaner import DataCleaner, CleaningOptions
from backend.app.data.profiler import DataProfiler
from backend.app.monitoring.logger import logger

# Import API routes
from backend.app.api.routes import auth, dashboard, analytics, datasets, reports, system

def seed_database():
    """Initializes schema and seeds demonstration benchmark data and default admin."""
    try:
        logger.info("Initializing database schema...")
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        logger.warning("Table creation skipped or handled: %s", e)
    
    try:
        db = SessionLocal()
        repo = DatabaseRepository(db)
        
        # 1. Seed Admin User if none exists
        try:
            admin = repo.get_user_by_email(settings.ADMIN_DEFAULT_EMAIL)
            if not admin:
                logger.info("Seeding default administrator (%s)...", settings.ADMIN_DEFAULT_EMAIL)
                repo.create_user(
                    email=settings.ADMIN_DEFAULT_EMAIL,
                    hashed_password=get_password_hash(settings.ADMIN_DEFAULT_PASSWORD),
                    full_name="System Administrator",
                    role="admin"
                )
                repo.log("INFO", f"Default admin {settings.ADMIN_DEFAULT_EMAIL} initialized", "Bootstrap")
        except Exception as e:
            logger.warning("Admin check skipped: %s", e)

        # 2. Seed Benchmark Dataset if no dataset exists
        try:
            datasets_list = repo.get_datasets()
            if not datasets_list:
                demo_csv = BASE_DIR / "data" / "raw" / "traffic_accidents_benchmark_demonstration.csv"
                if demo_csv.exists():
                    logger.info("Loading initial demonstration benchmark dataset (%s)...", demo_csv.name)
                    df, meta = DataLoader.load_file(demo_csv)
                    scorecard = DataProfiler.profile(df)
                    clean_opts = CleaningOptions()
                    cleaned_df, summary = DataCleaner.clean(df, clean_opts)
                    proc_path = settings.PROCESSED_DATA_DIR / "cleaned_benchmark_demonstration.parquet"
                    cleaned_df.to_parquet(proc_path, index=False)
                    dataset = repo.create_dataset(
                        name="Benchmark Demonstration Dataset (2020-2024)",
                        filename=demo_csv.name,
                        file_path=str(proc_path),
                        row_count=len(cleaned_df),
                        column_count=len(cleaned_df.columns),
                        origin="Benchmark Demonstration Dataset (Statistically Grounded)",
                        description="Standard multi-year road crash dataset with geo-coordinates, casualty counts, collision types, and road/weather conditions.",
                        is_active=True
                    )
                    repo.bulk_insert_records(dataset_id=dataset.id, df=cleaned_df)
                    repo.save_quality_report(
                        dataset_id=dataset.id,
                        total_records=scorecard.total_records,
                        missing_cells=scorecard.total_missing_cells,
                        duplicate_rows=scorecard.duplicate_count,
                        anomaly_count=scorecard.invalid_dates_count + scorecard.invalid_coords_count,
                        quality_score=scorecard.overall_score,
                        metrics_dict=scorecard.__dict__
                    )
                    repo.log("INFO", f"Seeded benchmark dataset with {len(cleaned_df)} records", "Bootstrap")
        except Exception as e:
            logger.warning("Dataset seed check skipped: %s", e)
        finally:
            db.close()
    except Exception as e:
        logger.warning("Database bootstrap skipped: %s", e)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Run bootstrap safely
    try:
        seed_database()
    except Exception as e:
        logger.warning("Lifespan startup handled: %s", e)
    yield
    # Shutdown
    logger.info("Shutting down TRAFFIC TREND backend.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="2.0.0",
    description="Institutional Road Safety Intelligence & Accident Analytics Platform API",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:[0-9]+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routes
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["Authentication"])
app.include_router(dashboard.router, prefix=f"{settings.API_V1_STR}/dashboard", tags=["Dashboard"])
app.include_router(analytics.router, prefix=f"{settings.API_V1_STR}/analytics", tags=["Analytics"])
app.include_router(datasets.router, prefix=f"{settings.API_V1_STR}/datasets", tags=["Datasets"])
app.include_router(reports.router, prefix=f"{settings.API_V1_STR}/reports", tags=["Reports"])
app.include_router(system.router, prefix=f"{settings.API_V1_STR}/system", tags=["System"])

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "traffic-trend-api", "version": "2.0.0"}

@app.get("/", tags=["Root"])
def root():
    return {
        "platform": "TRAFFIC TREND",
        "description": "Road Safety Intelligence & Accident Analytics Platform",
        "docs_url": "/docs",
        "api_v1": settings.API_V1_STR
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
