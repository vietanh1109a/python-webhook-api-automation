"""FastAPI application entry point and lifecycle setup."""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.database import init_db
from app.routers import exports, health, leads, stats, webhooks

# Configure application logging
LOG_DIR = Path("logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)
log_level = getattr(logging, settings.LOG_LEVEL, logging.INFO)

logging.basicConfig(
    level=log_level,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(LOG_DIR / "app.log", encoding="utf-8"),
    ],
)

logger = logging.getLogger("app.main")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifecycle events: startup and shutdown."""
    logger.info("Initializing application services and database...")
    init_db()
    logger.info(
        "Application started successfully. Enrichment mode: %s",
        settings.ENRICHMENT_MODE,
    )
    yield
    logger.info("Application shutting down...")


app = FastAPI(
    title="Lead Intake & API Automation Service",
    description=(
        "A lightweight Python automation service that receives lead webhooks, "
        "cleans and validates records, prevents duplicates, integrates with external "
        "APIs, stores structured data, and exports business-ready CSV/Excel reports."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# Enable CORS for external form integrations or dashboard clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Return clean, user-friendly JSON error details for validation failures."""
    logger.warning("Validation failed for %s: %s", request.url.path, exc.errors())
    errors = []
    for err in exc.errors():
        field = " -> ".join(str(loc) for loc in err.get("loc", []))
        errors.append({"field": field, "message": err.get("msg", "Invalid value")})
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={"detail": "Payload validation failed", "errors": errors},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all error handler ensuring stack traces are not leaked to API clients."""
    logger.exception("Unhandled error processing %s: %s", request.url.path, exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred while processing your request."},
    )


# Mount routers
app.include_router(health.router)
app.include_router(webhooks.router)
app.include_router(leads.router)
app.include_router(stats.router)
app.include_router(exports.router)
