"""Structured logging configuration using structlog."""

import logging
import sys
from src.core.settings import settings


def configure_logging() -> None:
    """Configure basic console logging"""

    # Set root log level
    log_level = getattr(logging, settings.log_level.upper())

    # Create handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )
    )

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.addHandler(handler)

    # Silence noisy libraries
    logging.getLogger("chromadb").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("transformers").setLevel(logging.WARNING)
    logging.getLogger("sentence_transformers").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a standard logger."""
    return logging.getLogger(name)
