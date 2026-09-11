"""Database CRUD operations for Leads and ProcessingEvents."""

import logging
from typing import Any, Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Lead, ProcessingEvent

logger = logging.getLogger(__name__)


def record_event(
    db: Session,
    event_type: str,
    status: str,
    lead_id: Optional[int] = None,
    message: Optional[str] = None,
) -> ProcessingEvent:
    """Create and persist a processing audit event."""
    event = ProcessingEvent(
        event_type=event_type,
        status=status,
        lead_id=lead_id,
        message=message,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def create_lead(
    db: Session,
    lead_data: dict[str, Any],
    enrichment_status: str = "pending",
    enrichment_score: Optional[float] = None,
    enrichment_segment: Optional[str] = None,
) -> Lead:
    """Create a new Lead record and commit to the database."""
    lead = Lead(
        name=lead_data["name"],
        email=lead_data["email"],
        external_id=lead_data.get("external_id"),
        company=lead_data.get("company"),
        source=lead_data.get("source", "unknown"),
        notes=lead_data.get("notes"),
        enrichment_status=enrichment_status,
        enrichment_score=enrichment_score,
        enrichment_segment=enrichment_segment,
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)

    logger.info("Lead created with ID: %s (email: %s)", lead.id, lead.email)
    return lead


def get_lead_by_id(db: Session, lead_id: int) -> Optional[Lead]:
    """Retrieve a single lead by primary key ID."""
    stmt = select(Lead).where(Lead.id == lead_id)
    return db.execute(stmt).scalars().first()


def list_leads(
    db: Session,
    page: int = 1,
    page_size: int = 50,
    source: Optional[str] = None,
) -> tuple[list[Lead], int]:
    """
    Retrieve a paginated list of leads with optional source filtering.
    Returns (items, total_count).
    """
    query = select(Lead)
    count_query = select(func.count(Lead.id))

    if source:
        query = query.where(Lead.source == source.strip().lower())
        count_query = count_query.where(Lead.source == source.strip().lower())

    total = db.execute(count_query).scalar() or 0

    offset = (page - 1) * page_size
    query = query.order_by(Lead.id.desc()).offset(offset).limit(page_size)
    items = list(db.execute(query).scalars().all())

    return items, total


def get_all_leads_for_export(db: Session) -> list[Lead]:
    """Retrieve all leads ordered by ID ascending for CSV and Excel export."""
    stmt = select(Lead).order_by(Lead.id.asc())
    return list(db.execute(stmt).scalars().all())


def get_processing_stats(db: Session) -> dict[str, Any]:
    """Calculate persistent processing and lead statistics."""
    total_leads = db.execute(select(func.count(Lead.id))).scalar() or 0

    def count_events(event_type: str) -> int:
        stmt = select(func.count(ProcessingEvent.id)).where(
            ProcessingEvent.event_type == event_type
        )
        return db.execute(stmt).scalar() or 0

    total_webhooks = count_events("webhook_received")
    created = count_events("lead_created")
    duplicates = count_events("duplicate_detected")
    enrichment_success = count_events("enrichment_success")
    enrichment_failed = count_events("enrichment_failed")

    # Group leads by source
    source_stmt = select(Lead.source, func.count(Lead.id)).group_by(Lead.source)
    source_rows = db.execute(source_stmt).all()
    leads_by_source = {row[0]: row[1] for row in source_rows}

    return {
        "total_leads": total_leads,
        "total_webhooks_received": total_webhooks,
        "created": created,
        "duplicates": duplicates,
        "enrichment_success": enrichment_success,
        "enrichment_failed": enrichment_failed,
        "leads_by_source": leads_by_source,
    }
