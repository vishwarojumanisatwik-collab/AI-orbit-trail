from src.config import (
    DATA_DIR,
    RAW_DATA_DIR,
    PROCESSED_DATA_DIR,
    FINAL_DATA_DIR,
    LOG_DIR,
)


def ensure_directories() -> None:
    """Create required project directories if they don't exist."""

    directories = [
        DATA_DIR,
        RAW_DATA_DIR,
        PROCESSED_DATA_DIR,
        FINAL_DATA_DIR,
        LOG_DIR,
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)