"""Health check endpoint."""

from fastapi import APIRouter

from app.schemas import HealthResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    """Check health status of the service."""
    return HealthResponse(status="ok")
