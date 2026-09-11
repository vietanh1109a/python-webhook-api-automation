"""REST endpoint for processing statistics."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.crud import get_processing_stats
from app.database import get_db
from app.schemas import StatsResponse

router = APIRouter(prefix="/api/stats", tags=["Statistics"])


@router.get("", response_model=StatsResponse)
def get_stats(db: Session = Depends(get_db)) -> StatsResponse:
    """Retrieve cumulative processing statistics and source breakdowns."""
    stats_data = get_processing_stats(db)
    return StatsResponse(**stats_data)
