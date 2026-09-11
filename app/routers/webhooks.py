"""Webhook ingestion router for lead records."""

import logging

from fastapi import APIRouter, Depends, Response, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.crud import create_lead, record_event
from app.database import get_db
from app.schemas import LeadWebhookPayload, WebhookResponse
from app.services.deduplication import find_duplicate_lead
from app.services.enrichment import get_enrichment_provider
from app.services.normalization import normalize_lead_payload

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


@router.post(
    "/leads",
    response_model=WebhookResponse,
    responses={
        200: {
            "model": WebhookResponse,
            "description": "Lead was detected as duplicate and not recreated.",
        },
        201: {
            "model": WebhookResponse,
            "description": "New lead was successfully validated, enriched, and stored.",
        },
    },
)
def ingest_lead_webhook(
    payload: LeadWebhookPayload,
    response: Response,
    db: Session = Depends(get_db),
) -> JSONResponse:
    """
    Ingest a lead payload from webhooks, normalize its fields, check for duplicates,
    perform optional API enrichment, and persist to database.
    """
    logger.info("Received incoming webhook for email: %s", payload.email)

    # 1. Audit event: webhook received
    record_event(
        db,
        event_type="webhook_received",
        status="received",
        message=f"Received webhook payload for source: {payload.source or 'unknown'}",
    )

    # 2. Normalize input data
    normalized = normalize_lead_payload(payload)

    # 3. Deduplication check
    duplicate = find_duplicate_lead(
        db,
        source=normalized["source"],
        email=normalized["email"],
        external_id=normalized["external_id"],
    )

    if duplicate:
        logger.info(
            "Duplicate lead detected (ID %d) for source: %s",
            duplicate.id,
            normalized["source"],
        )
        record_event(
            db,
            event_type="duplicate_detected",
            status="duplicate",
            lead_id=duplicate.id,
            message=f"Duplicate detected via source={normalized['source']}",
        )
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "duplicate",
                "lead_id": duplicate.id,
                "message": "Lead already exists",
            },
        )

    # 4. Enrichment
    enrichment_provider = get_enrichment_provider()
    enrichment_res = enrichment_provider.enrich(normalized)

    # 5. Persist lead
    new_lead = create_lead(
        db,
        lead_data=normalized,
        enrichment_status=enrichment_res.status,
        enrichment_score=enrichment_res.score,
        enrichment_segment=enrichment_res.segment,
    )

    # 6. Audit event: lead created
    record_event(
        db,
        event_type="lead_created",
        status="success",
        lead_id=new_lead.id,
        message=f"Created lead ID {new_lead.id} with source={new_lead.source}",
    )

    # 7. Audit event: enrichment outcome
    if enrichment_res.status == "enriched":
        record_event(
            db,
            event_type="enrichment_success",
            status="success",
            lead_id=new_lead.id,
            message=f"Enriched: score={enrichment_res.score}, segment={enrichment_res.segment}",
        )
    elif enrichment_res.status == "failed":
        record_event(
            db,
            event_type="enrichment_failed",
            status="failed",
            lead_id=new_lead.id,
            message=enrichment_res.error or "Enrichment request failed",
        )

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={
            "status": "created",
            "lead_id": new_lead.id,
            "message": "Lead created successfully",
        },
    )
