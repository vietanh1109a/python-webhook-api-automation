"""Deduplication logic for incoming leads."""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Lead


def find_duplicate_lead(
    db: Session,
    source: str,
    email: str,
    external_id: Optional[str] = None,
) -> Optional[Lead]:
    """
    Check for existing duplicate lead based on deterministic priority rules:

    1. If external_id exists: check (source + external_id)
    2. If external_id does not exist: check (source + normalized email)
    """
    if external_id:
        stmt = select(Lead).where(
            Lead.source == source,
            Lead.external_id == external_id,
        )
        existing = db.execute(stmt).scalars().first()
        if existing:
            return existing

    # Fallback to source + email if external_id is absent or if no external_id match was found
    if not external_id:
        stmt = select(Lead).where(
            Lead.source == source,
            Lead.email == email,
        )
        return db.execute(stmt).scalars().first()

    return None
