"""REST endpoints for querying leads."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.crud import get_lead_by_id, list_leads
from app.database import get_db
from app.schemas import LeadListResponse, LeadResponse

router = APIRouter(prefix="/api/leads", tags=["Leads"])


@router.get("", response_model=LeadListResponse)
def get_leads(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(50, ge=1, le=200, description="Items per page (max 200)"),
    source: Optional[str] = Query(None, description="Filter leads by source channel"),
    db: Session = Depends(get_db),
) -> LeadListResponse:
    """Retrieve a paginated list of leads with optional source filtering."""
    items, total = list_leads(db, page=page, page_size=page_size, source=source)
    return LeadListResponse(
        page=page,
        page_size=page_size,
        total=total,
        items=[LeadResponse.model_validate(item) for item in items],
    )


@router.get("/{lead_id}", response_model=LeadResponse)
def get_lead(
    lead_id: int,
    db: Session = Depends(get_db),
) -> LeadResponse:
    """Retrieve details for a single lead by ID."""
    lead = get_lead_by_id(db, lead_id)
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lead with ID {lead_id} was not found",
        )
    return LeadResponse.model_validate(lead)
