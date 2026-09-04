from pathlib import Path

from dotenv import load_dotenv


# Project root
BASE_DIR = Path(__file__).resolve().parent.parent

# Data directories
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
FINAL_DATA_DIR = DATA_DIR / "final"

# Logs
LOG_DIR = BASE_DIR / "logs"

# Environment
ENV_FILE = BASE_DIR / ".env"

load_dotenv(ENV_FILE)


# Pipeline configuration
PROJECT_NAME = "AI Orbit Data Pipeline"

SELECTED_MODULE = "tools"

REQUEST_TIMEOUT = 20.0

MAX_RETRIES = 3

USER_AGENT = (
    "AIOrbitDataPipeline/1.0 "
    "(data-quality-research; respectful-crawling)"
)
# Discovery sources
DISCOVERY_SOURCES = [
    {
        "name": "AI Tools Directory",
        "url": "https://theresanaiforthat.com/",
    },
]
# LLM configuration
LLM_PROVIDER = "openai"
LLM_MODEL = "gpt-5.6-luna"
LLM_DRY_RUN = True