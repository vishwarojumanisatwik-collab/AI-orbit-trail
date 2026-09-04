from src.utils.paths import ensure_directories
from src.utils.logging import setup_logging


def main() -> None:
    logger = setup_logging()

    ensure_directories()

    logger.info("AI Orbit Data Pipeline")
    logger.info("Pipeline initialized successfully.")


if __name__ == "__main__":
    main()