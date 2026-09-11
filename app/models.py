"""SQLAlchemy models for Lead and ProcessingEvent tables."""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def utc_now() -> datetime:
    """Return the current timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)


class Lead(Base):
    """Represents an ingested business lead."""

    __tablename__ = "leads"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    external_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    company: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    source: Mapped[str] = mapped_column(String(100), nullable=False, default="unknown", index=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False
    )

    enrichment_status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="pending"
    )
    enrichment_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    enrichment_segment: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Relationships
    events: Mapped[list["ProcessingEvent"]] = relationship(
        "ProcessingEvent", back_populates="lead", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Lead id={self.id} email={self.email!r} source={self.source!r}>"


class ProcessingEvent(Base):
    """Tracks persistent audit and processing statistics across the lead lifecycle."""

    __tablename__ = "processing_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    lead_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("leads.id", ondelete="SET NULL"), nullable=True, index=True
    )
    message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, nullable=False
    )

    lead: Mapped[Optional["Lead"]] = relationship("Lead", back_populates="events")

    def __repr__(self) -> str:
        return f"<ProcessingEvent id={self.id} type={self.event_type!r} status={self.status!r}>"
