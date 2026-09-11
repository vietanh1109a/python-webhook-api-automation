"""Tests for data normalization functions."""

from app.services.normalization import (
    collapse_spaces,
    normalize_email,
    normalize_lead_payload,
    normalize_name,
    normalize_source,
    normalize_string_field,
)


def test_collapse_spaces() -> None:
    assert collapse_spaces("   hello     world   ") == "hello world"
    assert collapse_spaces("single") == "single"
    assert collapse_spaces("  multiple   \t\n  spaces   ") == "multiple spaces"


def test_normalize_email_lowercasing() -> None:
    assert normalize_email(" JOHN.DOE@EXAMPLE.COM ") == "john.doe@example.com"
    assert normalize_email("  User@Domain.Co.UK  ") == "user@domain.co.uk"


def test_normalize_source_default_and_casing() -> None:
    assert normalize_source("  Shopify  ") == "shopify"
    assert normalize_source("WEBSITE") == "website"
    assert normalize_source("") == "unknown"
    assert normalize_source("   ") == "unknown"
    assert normalize_source(None) == "unknown"


def test_normalize_string_field_empty_to_none() -> None:
    assert normalize_string_field("   ") is None
    assert normalize_string_field(None) is None
    assert normalize_string_field(" Acme Corp ") == "Acme Corp"


def test_name_preserves_casing() -> None:
    # Names should NOT be converted to Title Case automatically
    assert normalize_name("  mC'Donald   O'Connor  ") == "mC'Donald O'Connor"
    assert normalize_name("  alice   vON   der  ") == "alice vON der"


def test_normalize_lead_payload_comprehensive() -> None:
    raw_payload = {
        "external_id": "   ext-9921   ",
        "name": "  Jane   McGregor ",
        "email": " JANE.MCGREGOR@Example.COM ",
        "company": "   ",
        "source": "  FACEBOOK  ",
        "notes": "  Looking for   custom pricing   ",
    }
    normalized = normalize_lead_payload(raw_payload)

    assert normalized["external_id"] == "ext-9921"
    assert normalized["name"] == "Jane McGregor"
    assert normalized["email"] == "jane.mcgregor@example.com"
    assert normalized["company"] is None
    assert normalized["source"] == "facebook"
    assert normalized["notes"] == "Looking for custom pricing"
