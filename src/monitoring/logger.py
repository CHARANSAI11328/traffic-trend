"""
Centralized Logging and Telemetry for TRAFFIC TREND Platform
"""
import logging
import sys
from pathlib import Path
from src.utils.configuration import LOG_FILE_PATH, LOG_LEVEL

_LOGGER_INITIALIZED = False

def setup_logger(name: str = "traffic_trend") -> logging.Logger:
    """Configures and returns a thread-safe structured logger."""
    global _LOGGER_INITIALIZED
    logger = logging.getLogger(name)

    if not _LOGGER_INITIALIZED:
        logger.setLevel(getattr(logging, LOG_LEVEL.upper(), logging.INFO))

        # Formatters
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] [%(name)s:%(lineno)d] - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        # File Handler with UTF-8
        try:
            LOG_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(LOG_FILE_PATH, encoding="utf-8")
            file_handler.setLevel(getattr(logging, LOG_LEVEL.upper(), logging.INFO))
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            sys.stderr.write(f"Warning: Could not bind log file handler: {e}\n")

        # Stream Handler (Console)
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setLevel(getattr(logging, LOG_LEVEL.upper(), logging.INFO))
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

        logger.propagate = False
        _LOGGER_INITIALIZED = True

    return logger

logger = setup_logger()

