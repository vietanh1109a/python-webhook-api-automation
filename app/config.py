"""Application configuration module."""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Settings:
    """Application settings loaded from environment variables."""

    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./data/leads.db")
    ENRICHMENT_MODE: str = os.getenv("ENRICHMENT_MODE", "mock").strip().lower()
    ENRICHMENT_API_URL: str = os.getenv("ENRICHMENT_API_URL", "").strip()
    ENRICHMENT_API_KEY: str = os.getenv("ENRICHMENT_API_KEY", "").strip()
    ENRICHMENT_TIMEOUT_SECONDS: float = float(os.getenv("ENRICHMENT_TIMEOUT_SECONDS", "5.0"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").strip().upper()


settings = Settings()
