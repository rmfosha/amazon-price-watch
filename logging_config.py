"""
Logging configuration.

This module sets up logging to both a rotating file and the console, ensuring that logs are
formatted and stored appropriately for debugging and monitoring purposes.
"""
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_DIR = Path('logs')
LOG_DIR.mkdir(exist_ok=True)

LOG_FILE = LOG_DIR / 'app.log'


def setup_logging(level=logging.INFO):
    """
    Configure logging.

    Sets up logging to a rotating file and the console with a consistent format.

    Args:
        level (int, optional): The logging level (e.g., logging.INFO, logging.DEBUG).
        Defaults to logging.INFO.
    """
    formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )

    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=2_000_000,   # 2 MB
        backupCount=5,
        encoding='utf-8',
    )
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(level)
    root.handlers.clear()  # avoid duplicate logs
    root.addHandler(file_handler)
    root.addHandler(console_handler)
