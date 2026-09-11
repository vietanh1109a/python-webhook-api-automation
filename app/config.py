"""Application configuration module."""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


def normalize_database_url(url: str) -> str:
    """Normalize common PostgreSQL URLs for compatibility with psycopg v3."""
    url = url.strip()
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg://", 1)
    return url


@dataclass(frozen=True)
class Settings:
    """Application settings loaded from environment variables."""

    DATABASE_URL: str = normalize_database_url(
        os.getenv("DATABASE_URL", "sqlite:///./data/leads.db")
    )
    ENRICHMENT_MODE: str = os.getenv("ENRICHMENT_MODE", "mock").strip().lower()
    ENRICHMENT_API_URL: str = os.getenv("ENRICHMENT_API_URL", "").strip()
    ENRICHMENT_API_KEY: str = os.getenv("ENRICHMENT_API_KEY", "").strip()
    ENRICHMENT_TIMEOUT_SECONDS: float = float(os.getenv("ENRICHMENT_TIMEOUT_SECONDS", "5.0"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").strip().upper()


settings = Settings()
