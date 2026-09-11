"""Pydantic schemas for request validation and response serialization."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class LeadWebhookPayload(BaseModel):
    """Payload schema for incoming lead webhooks."""

    name: str = Field(..., min_length=1, max_length=255, description="Full name of the contact")
    email: EmailStr = Field(..., max_length=255, description="Valid contact email address")
    external_id: Optional[str] = Field(
        None, max_length=255, description="External reference ID from source CRM/platform"
    )
    company: Optional[str] = Field(None, max_length=255, description="Company or organization name")
    source: Optional[str] = Field(
        "unknown", max_length=100, description="Source channel (e.g., website, shopify, facebook)"
    )
    notes: Optional[str] = Field(None, description="Initial notes or inquiry details")


class WebhookResponse(BaseModel):
    """Response returned after processing an ingested webhook."""

    status: str = Field(..., description="'created' or 'duplicate'")
    lead_id: int = Field(..., description="Database ID of the lead")
    message: str = Field(..., description="Human-readable processing summary")


class LeadResponse(BaseModel):
    """Detailed representation of a stored lead."""

    id: int
    external_id: Optional[str] = None
    name: str
    email: str
    company: Optional[str] = None
    source: str
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    enrichment_status: str
    enrichment_score: Optional[float] = None
    enrichment_segment: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class LeadListResponse(BaseModel):
    """Paginated list of leads."""

    page: int
    page_size: int
    total: int
    items: list[LeadResponse]


class StatsResponse(BaseModel):
    """Processing and audit statistics."""

    total_leads: int
    total_webhooks_received: int
    created: int
    duplicates: int
    enrichment_success: int
    enrichment_failed: int
    leads_by_source: dict[str, int]


class HealthResponse(BaseModel):
    """Health check status."""

    status: str = "ok"
