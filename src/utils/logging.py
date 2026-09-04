import logging
from pathlib import Path

from src.config import LOG_DIR


def setup_logging() -> logging.Logger:
    """Configure application logging."""

    LOG_DIR.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("ai_orbit")
    logger.setLevel(logging.INFO)

    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(
        Path(LOG_DIR) / "pipeline.log",
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger