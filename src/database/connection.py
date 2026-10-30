"""
Database Engine & Session Management for TRAFFIC TREND Platform
"""
from contextlib import contextmanager
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from src.utils.configuration import DATABASE_URL
from src.monitoring.logger import logger
from src.database.models import Base

# Engine configuration - SQLite needs check_same_thread=False for multi-threaded Streamlit
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)

def init_db() -> None:
    """Initializes tables in database if they do not exist."""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}", exc_info=True)
        raise

@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """Context manager for safe database transactions with auto-rollback on error."""
    session: Session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database transaction rolled back due to error: {e}", exc_info=True)
        raise
    finally:
        session.close()

def check_database_health() -> dict:
    """Verifies database connectivity and returns latency metadata."""
    import time
    from sqlalchemy import text
    start_time = time.time()
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        latency_ms = round((time.time() - start_time) * 1000, 2)
        return {
            "status": "HEALTHY",
            "connected": True,
            "latency_ms": latency_ms,
            "dialect": engine.dialect.name,
            "url": str(DATABASE_URL).split("@")[-1]  # Mask credentials
        }
    except Exception as e:
        return {
            "status": "UNHEALTHY",
            "connected": False,
            "latency_ms": -1,
            "error": str(e)
        }
