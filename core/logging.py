# core/logging.py
"""Centralized logging configuration for Nexomate.

Provides structured, consistent logging across all modules (console + rotating file).
"""

import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

_initialized = False


def setup_logging(default_level: str = None) -> None:
    """Initialize application-wide root logging handler."""
    global _initialized
    if _initialized:
        return

    level_str = (default_level or os.getenv("LOG_LEVEL", "INFO")).upper()
    level = getattr(logging, level_str, logging.INFO)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Avoid duplicate handlers if Streamlit or another framework reloads
    if not root_logger.handlers:
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # 1. Console Handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

        # 2. File Handler (Rotating)
        try:
            log_dir = Path(__file__).resolve().parent.parent / "logs"
            log_dir.mkdir(parents=True, exist_ok=True)
            log_file = log_dir / "nexomate.log"
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=5 * 1024 * 1024,  # 5 MB
                backupCount=3,
                encoding="utf-8",
            )
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
        except Exception:
            # Fall back to console only if file handler cannot be created (e.g., read-only filesystem)
            pass

    _initialized = True


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance configured with Nexomate defaults."""
    if not _initialized:
        setup_logging()
    return logging.getLogger(name)
