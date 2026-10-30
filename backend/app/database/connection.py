import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from backend.app.core.config import settings

logger = logging.getLogger(__name__)

# Normalize Database URL for SQLAlchemy 2.0+
db_url = settings.DATABASE_URL
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql+psycopg2://", 1)
elif db_url.startswith("postgresql://") and not db_url.startswith("postgresql+"):
    db_url = db_url.replace("postgresql://", "postgresql+psycopg2://", 1)

# Engine kwargs based on driver
engine_kwargs = {"echo": False}
if "sqlite" in db_url:
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    # PostgreSQL pooling parameters
    engine_kwargs.update({
        "pool_pre_ping": True,
        "pool_size": 10,
        "max_overflow": 20,
        "pool_recycle": 1800,
    })

try:
    engine = create_engine(db_url, **engine_kwargs)
    logger.info("Database engine initialized with URL: %s", db_url.split("@")[-1] if "@" in db_url else db_url)
except Exception as e:
    logger.warning("Failed to initialize primary database %s, falling back to SQLite: %s", db_url, e)
    fallback_url = f"sqlite:///{settings.DATABASE_DIR}/traffic_trend.db"
    engine = create_engine(fallback_url, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """Dependency that provides a database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
