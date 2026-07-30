"""
Centralized logging configuration module.
"""

import logging
from pathlib import Path
import sys

_DEFAULT_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logger(
    name: str = "library",
    log_level: int = logging.INFO,
    log_file: Path | str | None = None,
) -> logging.Logger:
    """Configures and returns a logger instance.

    Args:
        name: Logger module name.
        log_level: Numeric logging level (e.g. logging.INFO).
        log_file: Optional file path to write log messages.

    Returns:
        Configured logging.Logger object.
    """
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    # Prevent duplicate handlers if function is called multiple times
    if logger.handlers:
        return logger

    formatter = logging.Formatter(_DEFAULT_LOG_FORMAT, datefmt=_DEFAULT_DATE_FORMAT)

    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Optional File Handler
    if log_file:
        file_path = Path(log_file)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(file_path, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str = "library") -> logging.Logger:
    """Retrieves an existing named logger or returns default."""
    return logging.getLogger(name)
