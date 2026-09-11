"""Tests for webhook ingestion endpoint."""

from fastapi.testclient import TestClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Lead, ProcessingEvent


def test_create_valid_lead_returns_201(client: TestClient, db_session: Session) -> None:
    payload = {
        "external_id": "shopify-101",
        "name": "  John   Doe ",
        "email": " JOHN.DOE@example.com ",
        "company": "  Acme Corp  ",
        "source": " Shopify ",
        "notes": "  Interested in enterprise plan  ",
    }
    response = client.post("/webhooks/leads", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "created"
    assert "lead_id" in data
    lead_id = data["lead_id"]

    # Verify database persistence
    lead = db_session.get(Lead, lead_id)
    assert lead is not None
    assert lead.name == "John Doe"
    assert lead.email == "john.doe@example.com"
    assert lead.company == "Acme Corp"
    assert lead.source == "shopify"
    assert lead.notes == "Interested in enterprise plan"


def test_default_source_becomes_unknown(client: TestClient, db_session: Session) -> None:
    payload = {
        "name": "Sarah Connor",
        "email": "sarah@cyberdyne.com",
    }
    response = client.post("/webhooks/leads", json=payload)
    assert response.status_code == 201
    lead_id = response.json()["lead_id"]

    lead = db_session.get(Lead, lead_id)
    assert lead is not None
    assert lead.source == "unknown"


def test_duplicate_by_external_id_detected(client: TestClient, db_session: Session) -> None:
    lead_payload = {
        "external_id": "crm-5501",
        "name": "David Miller",
        "email": "david@miller.com",
        "source": "hubspot",
    }
    # First submission
    res1 = client.post("/webhooks/leads", json=lead_payload)
    assert res1.status_code == 201
    first_id = res1.json()["lead_id"]

    # Second submission with different email/name casing but identical source + external_id
    dup_payload = {
        "external_id": "  crm-5501  ",
        "name": "David M. Miller",
        "email": "different.david@miller.com",
        "source": "  HUBSPOT  ",
    }
    res2 = client.post("/webhooks/leads", json=dup_payload)
    assert res2.status_code == 200
    assert res2.json() == {
        "status": "duplicate",
        "lead_id": first_id,
        "message": "Lead already exists",
    }

    # Verify no second row was inserted
    count = db_session.execute(select(func.count(Lead.id))).scalar()
    assert count == 1


def test_duplicate_by_email_when_external_id_absent(
    client: TestClient, db_session: Session
) -> None:
    lead_payload = {
        "name": "Emily Watson",
        "email": "emily@example.org",
        "source": "website",
    }
    res1 = client.post("/webhooks/leads", json=lead_payload)
    assert res1.status_code == 201
    first_id = res1.json()["lead_id"]

    # Duplicate without external_id, same source and email with spaces and upper case
    dup_payload = {
        "name": "Emily Watson",
        "email": "  EMILY@EXAMPLE.ORG  ",
        "source": "  WEBSITE  ",
    }
    res2 = client.post("/webhooks/leads", json=dup_payload)
    assert res2.status_code == 200
    assert res2.json()["status"] == "duplicate"
    assert res2.json()["lead_id"] == first_id

    # Verify single database row
    count = db_session.execute(select(func.count(Lead.id))).scalar()
    assert count == 1


def test_invalid_email_returns_422_without_crash(client: TestClient) -> None:
    payload = {
        "name": "Bad Email User",
        "email": "not-an-email",
        "source": "website",
    }
    response = client.post("/webhooks/leads", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert "detail" in data
    assert "errors" in data


def test_missing_required_name_returns_422(client: TestClient) -> None:
    payload = {
        "email": "valid@email.com",
        "source": "website",
    }
    response = client.post("/webhooks/leads", json=payload)
    assert response.status_code == 422


def test_audit_events_recorded_on_webhook(client: TestClient, db_session: Session) -> None:
    payload = {
        "name": "Audit Test",
        "email": "audit@test.com",
        "source": "test",
    }
    res = client.post("/webhooks/leads", json=payload)
    assert res.status_code == 201

    events = db_session.execute(select(ProcessingEvent)).scalars().all()
    event_types = [e.event_type for e in events]
    assert "webhook_received" in event_types
    assert "lead_created" in event_types
