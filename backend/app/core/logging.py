import logging
import sys
from typing import Any

from app.core.config import settings


class StructuredFormatter(logging.Formatter):
    """Custom formatter providing clear structured logs with timestamps."""

    def __init__(self, fmt: str | None = None, datefmt: str | None = None):
        super().__init__(
            fmt=fmt or "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt=datefmt or "%Y-%m-%d %H:%M:%S",
        )


def setup_logging() -> None:
    """Configures structured logging for the application."""
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO

    formatter = StructuredFormatter()

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Avoid duplicate handlers if setup_logging is called multiple times
    if not root_logger.handlers:
        root_logger.addHandler(handler)
    else:
        root_logger.handlers = [handler]

    # Silence overly verbose third-party loggers if needed
    logging.getLogger("uvicorn.access").setLevel(log_level)


def get_logger(name: str) -> logging.Logger:
    """Utility helper to get a named logger."""
    return logging.getLogger(name)
