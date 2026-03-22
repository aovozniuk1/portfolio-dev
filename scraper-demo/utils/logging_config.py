"""Logging configuration with rotating file handler."""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging(level: str = "INFO", log_dir: str = "logs") -> logging.Logger:
    """Configure application logging with console and rotating file outputs.

    Args:
        level: Logging level name (DEBUG, INFO, WARNING, ERROR).
        log_dir: Directory for log files.

    Returns:
        The root logger instance.
    """
    Path(log_dir).mkdir(exist_ok=True)

    log_format = "%(asctime)s [%(levelname)-8s] %(name)s: %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(logging.Formatter(log_format, datefmt=date_format))
    root_logger.addHandler(console)

    file_handler = RotatingFileHandler(
        filename=f"{log_dir}/scraper.log",
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setFormatter(logging.Formatter(log_format, datefmt=date_format))
    root_logger.addHandler(file_handler)

    return root_logger
