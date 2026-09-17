"""
core/logger.py
Simple colored logger used across the framework.
"""

import logging

_LEVEL_COLORS = {
    "DEBUG": "\033[94m",
    "INFO": "\033[92m",
    "WARNING": "\033[93m",
    "ERROR": "\033[91m",
    "CRITICAL": "\033[95m",
}
_RESET = "\033[0m"


class ColorFormatter(logging.Formatter):
    def format(self, record):
        color = _LEVEL_COLORS.get(record.levelname, "")
        record.levelname = f"{color}{record.levelname}{_RESET}"
        return super().format(record)


def get_logger(name: str = "webscraper_pro", level: str = "INFO") -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(ColorFormatter("[%(asctime)s] %(levelname)s - %(message)s", "%H:%M:%S"))
        logger.addHandler(handler)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    logger.propagate = False
    return logger
