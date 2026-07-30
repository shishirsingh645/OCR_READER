"""
logger.py
---------

Centralized logging configuration for the OCR Reader project.

Features
--------
- Console logging
- File logging
- Singleton logger
- UTF-8 support
- Thread-safe
"""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from datetime import datetime
import config


_LOGGER_INITIALIZED = False
_CURRENT_LOG_FILE = None

def _initialize_logger(log_file: Path | None = None) -> None:
    """
    Configure the root logger.

    This function is called only once.
    """

    global _LOGGER_INITIALIZED

    if _LOGGER_INITIALIZED:
        return

    config.LOG_DIR.mkdir(parents=True, exist_ok=True)

    global _CURRENT_LOG_FILE

    if log_file is None:

        if _CURRENT_LOG_FILE is None:

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            _CURRENT_LOG_FILE = (
                config.LOG_DIR /
                f"OCR_{timestamp}.log"
            )

        log_file = _CURRENT_LOG_FILE

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    file_handler = RotatingFileHandler(
        filename=log_file,
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    root_logger = logging.getLogger()

    root_logger.setLevel(config.LOG_LEVEL)

    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    _LOGGER_INITIALIZED = True


def get_logger(name: str,log_file: Path | None = None,) -> logging.Logger:
    """
    Return a configured logger.

    Parameters
    ----------
    name : str
        Module name.

    Returns
    -------
    logging.Logger
    """

    _initialize_logger(log_file)

    return logging.getLogger(name)
def get_log_file() -> Path | None:
    """
    Return current log file.
    """

    return _CURRENT_LOG_FILE