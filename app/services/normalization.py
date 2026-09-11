"""Data cleaning and normalization service for lead records."""

from typing import Any, Optional

from app.schemas import LeadWebhookPayload


def collapse_spaces(text: str) -> str:
    """Strip leading/trailing whitespace and collapse internal repeated spaces to a single space."""
    return " ".join(text.strip().split())


def normalize_string_field(value: Optional[str]) -> Optional[str]:
    """Strip whitespace and collapse spaces. Return None if the resulting string is empty."""
    if value is None:
        return None
    collapsed = collapse_spaces(value)
    return collapsed if collapsed else None


def normalize_name(name: str) -> str:
    """Normalize whitespace in name while strictly preserving original casing."""
    return collapse_spaces(name)


def normalize_email(email: str) -> str:
    """Normalize whitespace and lowercase the email address."""
    return collapse_spaces(email).lower()


def normalize_source(source: Optional[str]) -> str:
    """Normalize whitespace, lowercase source, and default empty/missing values to 'unknown'."""
    cleaned = normalize_string_field(source)
    if cleaned is None:
        return "unknown"
    return cleaned.lower()


def normalize_lead_payload(payload: LeadWebhookPayload | dict[str, Any]) -> dict[str, Any]:
    """
    Apply comprehensive normalization rules to an ingested lead payload.

    Rules applied:
    1. Strip leading and trailing whitespace.
    2. Collapse repeated internal spaces.
    3. Emails must be lower-case.
    4. Source should be trimmed and lower-case (defaults to 'unknown' if empty).
    5. Empty optional strings become None.
    6. Do NOT aggressively modify names (preserve case).
    7. Notes should be trimmed and internal whitespace normalized.
    """
    if isinstance(payload, LeadWebhookPayload):
        raw_name = payload.name
        raw_email = str(payload.email)
        raw_external_id = payload.external_id
        raw_company = payload.company
        raw_source = payload.source
        raw_notes = payload.notes
    else:
        raw_name = payload.get("name", "")
        raw_email = str(payload.get("email", ""))
        raw_external_id = payload.get("external_id")
        raw_company = payload.get("company")
        raw_source = payload.get("source")
        raw_notes = payload.get("notes")

    return {
        "name": normalize_name(raw_name),
        "email": normalize_email(raw_email),
        "external_id": normalize_string_field(raw_external_id),
        "company": normalize_string_field(raw_company),
        "source": normalize_source(raw_source),
        "notes": normalize_string_field(raw_notes),
    }
