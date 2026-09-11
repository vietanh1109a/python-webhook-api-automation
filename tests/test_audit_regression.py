"""Comprehensive regression tests for audit findings:
- Database-level uniqueness & race condition safety
- Symmetric, order-independent deduplication
- Field length boundary validation
- Concurrent duplicate collision handling
- Transaction rollback & session usability
"""

import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, func, select
from sqlalchemy.orm import Session, sessionmaker

from app.database import Base, get_db
from app.main import app
from app.models import Lead, ProcessingEvent


def test_email_duplicate_case_insensitive(client: TestClient, db_session: Session) -> None:
    """Verify duplicate detection is case-insensitive on email within the same source."""
    payload1 = {"name": "User One", "email": "CASE@example.com", "source": "shopify"}
    res1 = client.post("/webhooks/leads", json=payload1)
    assert res1.status_code == 201
    first_id = res1.json()["lead_id"]

    payload2 = {"name": "User One", "email": "case@example.com", "source": "shopify"}
    res2 = client.post("/webhooks/leads", json=payload2)
    assert res2.status_code == 200
    assert res2.json()["status"] == "duplicate"
    assert res2.json()["lead_id"] == first_id

    count = db_session.execute(select(func.count(Lead.id))).scalar()
    assert count == 1


def test_external_id_duplicate(client: TestClient, db_session: Session) -> None:
    """Verify duplicate detection on source + external_id."""
    payload1 = {
        "external_id": "crm-ext-88",
        "name": "Alex Smith",
        "email": "alex1@example.com",
        "source": "hubspot",
    }
    res1 = client.post("/webhooks/leads", json=payload1)
    assert res1.status_code == 201
    lead_id = res1.json()["lead_id"]

    payload2 = {
        "external_id": "crm-ext-88",
        "name": "Alex Different Name",
        "email": "alex2@example.com",
        "source": "hubspot",
    }
    res2 = client.post("/webhooks/leads", json=payload2)
    assert res2.status_code == 200
    assert res2.json()["status"] == "duplicate"
    assert res2.json()["lead_id"] == lead_id

    count = db_session.execute(select(func.count(Lead.id))).scalar()
    assert count == 1


def test_external_id_lookup_falls_back_to_email(client: TestClient, db_session: Session) -> None:
    """Verify incoming payload with new external_id matches existing lead if source+email match."""
    payload1 = {
        "external_id": "shopify-old-id",
        "name": "Morgan Lee",
        "email": "morgan@example.com",
        "source": "shopify",
    }
    res1 = client.post("/webhooks/leads", json=payload1)
    assert res1.status_code == 201
    first_id = res1.json()["lead_id"]

    # Different external_id, same source + email
    payload2 = {
        "external_id": "shopify-new-id",
        "name": "Morgan Lee",
        "email": "morgan@example.com",
        "source": "shopify",
    }
    res2 = client.post("/webhooks/leads", json=payload2)
    assert res2.status_code == 200
    assert res2.json()["status"] == "duplicate"
    assert res2.json()["lead_id"] == first_id

    count = db_session.execute(select(func.count(Lead.id))).scalar()
    assert count == 1


def test_order_a_deduplication(client: TestClient, db_session: Session) -> None:
    """Order A: Ingest without external_id first, then same email with external_id."""
    payload1 = {
        "name": "Taylor Swift",
        "email": "taylor@music.com",
        "source": "website",
    }
    res1 = client.post("/webhooks/leads", json=payload1)
    assert res1.status_code == 201
    lead_id = res1.json()["lead_id"]

    payload2 = {
        "external_id": "web-order-a-99",
        "name": "Taylor Swift",
        "email": "taylor@music.com",
        "source": "website",
    }
    res2 = client.post("/webhooks/leads", json=payload2)
    assert res2.status_code == 200
    assert res2.json()["status"] == "duplicate"
    assert res2.json()["lead_id"] == lead_id

    count = db_session.execute(select(func.count(Lead.id))).scalar()
    assert count == 1


def test_order_b_deduplication(client: TestClient, db_session: Session) -> None:
    """Order B: Ingest with external_id first, then same email without external_id."""
    payload1 = {
        "external_id": "web-order-b-99",
        "name": "Jordan Bell",
        "email": "jordan@startup.io",
        "source": "website",
    }
    res1 = client.post("/webhooks/leads", json=payload1)
    assert res1.status_code == 201
    lead_id = res1.json()["lead_id"]

    payload2 = {
        "name": "Jordan Bell",
        "email": "jordan@startup.io",
        "source": "website",
    }
    res2 = client.post("/webhooks/leads", json=payload2)
    assert res2.status_code == 200
    assert res2.json()["status"] == "duplicate"
    assert res2.json()["lead_id"] == lead_id

    count = db_session.execute(select(func.count(Lead.id))).scalar()
    assert count == 1


def test_maximum_valid_field_lengths(client: TestClient, db_session: Session) -> None:
    """Verify input fields at the exact maximum boundary lengths (255 / 100) are accepted."""
    max_name = "N" * 255
    max_external_id = "E" * 255
    max_company = "C" * 255
    max_source = "s" * 100
    # Valid email up to RFC 5321 maximum length (254 chars, max 64 local part)
    max_email = ("u" * 64) + "@" + ("a" * 60) + "." + ("b" * 60) + "." + ("c" * 63) + ".com"
    long_notes = "Important inquiry notes. " * 100  # Text column allows long notes

    payload = {
        "name": max_name,
        "email": max_email,
        "external_id": max_external_id,
        "company": max_company,
        "source": max_source,
        "notes": long_notes,
    }
    response = client.post("/webhooks/leads", json=payload)
    assert response.status_code == 201
    lead_id = response.json()["lead_id"]

    lead = db_session.get(Lead, lead_id)
    assert lead is not None
    assert len(lead.name) == 255
    assert len(lead.email) == 254
    assert len(lead.external_id) == 255
    assert len(lead.company) == 255
    assert len(lead.source) == 100


def test_over_limit_fields_return_422(client: TestClient) -> None:
    """Verify that inputs exceeding String column lengths are rejected with HTTP 422."""
    # Name exceeding 255
    res_name = client.post(
        "/webhooks/leads",
        json={"name": "A" * 256, "email": "valid@email.com", "source": "test"},
    )
    assert res_name.status_code == 422
    assert "name" in str(res_name.json())

    # External ID exceeding 255
    res_ext = client.post(
        "/webhooks/leads",
        json={"name": "Valid Name", "email": "valid@email.com", "external_id": "X" * 256},
    )
    assert res_ext.status_code == 422
    assert "external_id" in str(res_ext.json())

    # Company exceeding 255
    res_comp = client.post(
        "/webhooks/leads",
        json={"name": "Valid Name", "email": "valid@email.com", "company": "C" * 256},
    )
    assert res_comp.status_code == 422
    assert "company" in str(res_comp.json())

    # Source exceeding 100
    res_source = client.post(
        "/webhooks/leads",
        json={"name": "Valid Name", "email": "valid@email.com", "source": "s" * 101},
    )
    assert res_source.status_code == 422
    assert "source" in str(res_source.json())


def test_integrity_error_duplicate_collision_returns_200(
    client: TestClient, db_session: Session, monkeypatch
) -> None:
    """Simulate a database race condition where create_lead raises IntegrityError."""
    # Pre-create lead
    existing = Lead(
        name="Collision User",
        email="collision@example.com",
        source="shopify",
        enrichment_status="enriched",
    )
    db_session.add(existing)
    db_session.commit()
    db_session.refresh(existing)

    # Ingest duplicate payload
    payload = {
        "name": "Collision User",
        "email": "collision@example.com",
        "source": "shopify",
    }
    response = client.post("/webhooks/leads", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "duplicate"
    assert data["lead_id"] == existing.id
    assert data["message"] == "Lead already exists"


def test_session_remains_usable_after_duplicate_collision(
    client: TestClient, db_session: Session
) -> None:
    """Verify that a session recovers via rollback and can continue processing distinct leads."""
    # 1. Ingest Lead A
    res_a = client.post(
        "/webhooks/leads",
        json={"name": "User Alpha", "email": "alpha@example.com", "source": "web"},
    )
    assert res_a.status_code == 201

    # 2. Ingest duplicate of Lead A
    res_dup = client.post(
        "/webhooks/leads",
        json={"name": "User Alpha", "email": "alpha@example.com", "source": "web"},
    )
    assert res_dup.status_code == 200
    assert res_dup.json()["status"] == "duplicate"

    # 3. Immediately ingest distinct Lead B in the same session environment
    res_b = client.post(
        "/webhooks/leads",
        json={"name": "User Beta", "email": "beta@example.com", "source": "web"},
    )
    assert res_b.status_code == 201
    assert res_b.json()["status"] == "created"

    # Verify both distinct leads are in the database
    leads = db_session.execute(select(Lead)).scalars().all()
    emails = {item.email for item in leads}
    assert emails == {"alpha@example.com", "beta@example.com"}


def test_concurrent_duplicate_attempts_file_sqlite() -> None:
    """
    Test real concurrent duplicate attempts against a file-based SQLite database with WAL.
    10 simultaneous requests with the identical lead payload must result in:
    - Exactly 1 Lead row created in DB
    - Exactly 1 response with HTTP 201
    - Exactly 9 responses with HTTP 200 (duplicate)
    - Zero HTTP 500 errors
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "concurrent_leads.db"
        file_db_url = f"sqlite:///{db_path.as_posix()}"

        file_engine = create_engine(
            file_db_url,
            connect_args={"check_same_thread": False, "timeout": 30.0},
        )
        Base.metadata.create_all(bind=file_engine)

        FileSession = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=file_engine,
        )

        def file_get_db():
            session = FileSession()
            try:
                yield session
            finally:
                session.close()

        app.dependency_overrides[get_db] = file_get_db

        payload = {
            "external_id": "race-1001",
            "name": "Race Tester",
            "email": "race@example.com",
            "source": "shopify",
            "company": "Fast Cars LLC",
        }

        def send_request(_: int):
            with TestClient(app) as test_client:
                return test_client.post("/webhooks/leads", json=payload)

        try:
            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(send_request, i) for i in range(10)]
                responses = [f.result() for f in futures]

            status_codes = [r.status_code for r in responses]
            statuses = [r.json().get("status") for r in responses]

            # Verify no 500 errors occurred
            assert 500 not in status_codes, f"500 error found in responses: {status_codes}"

            # Exactly one created (HTTP 201), nine duplicates (HTTP 200)
            c201 = status_codes.count(201)
            c200 = status_codes.count(200)
            assert c201 == 1, f"Expected 1 created, got {c201}"
            assert c200 == 9, f"Expected 9 duplicates, got {c200}"
            assert statuses.count("created") == 1
            assert statuses.count("duplicate") == 9

            # Verify the database has exactly 1 Lead row
            with FileSession() as check_session:
                leads_count = check_session.execute(select(func.count(Lead.id))).scalar()
                assert leads_count == 1, f"Expected exactly 1 Lead row, found {leads_count}"

                # Verify duplicate events were audited
                dup_events = check_session.execute(
                    select(func.count(ProcessingEvent.id)).where(
                        ProcessingEvent.event_type == "duplicate_detected"
                    )
                ).scalar()
                assert dup_events == 9, f"Expected 9 duplicate events, found {dup_events}"

        finally:
            app.dependency_overrides.clear()
            file_engine.dispose()
