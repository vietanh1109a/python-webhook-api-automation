"""Tests for lead enrichment service in off, mock, and HTTP modes."""

import httpx
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Lead, ProcessingEvent
from app.services.enrichment import (
    HttpEnrichmentProvider,
    MockEnrichmentProvider,
    OffEnrichmentProvider,
)


def test_mock_enrichment_provider() -> None:
    provider = MockEnrichmentProvider()

    # High tier lead
    lead_high = {
        "name": "CEO Jane",
        "company": "Enterprise Global",
        "source": "website",
        "notes": "Budget $50k",
        "external_id": "ent-1",
    }
    res_high = provider.enrich(lead_high)
    assert res_high.status == "enriched"
    assert res_high.score is not None
    assert res_high.score >= 75.0
    assert res_high.segment == "high"

    # Minimal lead
    lead_low = {
        "name": "Solo Dev",
        "company": None,
        "source": "other",
        "notes": None,
    }
    res_low = provider.enrich(lead_low)
    assert res_low.status == "enriched"
    assert res_low.score is not None
    assert res_low.score < 50.0
    assert res_low.segment == "low"


def test_off_enrichment_provider() -> None:
    provider = OffEnrichmentProvider()
    res = provider.enrich({"name": "Test", "email": "test@test.com"})
    assert res.status == "disabled"
    assert res.score is None
    assert res.segment is None


def test_http_enrichment_success_mock_transport() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers.get("authorization") == "Bearer test-mock-key"
        return httpx.Response(200, json={"score": 88.5, "segment": "high"})

    transport = httpx.MockTransport(handler)
    provider = HttpEnrichmentProvider(
        api_url="https://mock-enrichment.local/api/v1/enrich",
        api_key="test-mock-key",
        transport=transport,
        backoff_delays=[0.01, 0.02, 0.03],
    )

    res = provider.enrich({"name": "Http User", "email": "user@http.com"})
    assert res.status == "enriched"
    assert res.score == 88.5
    assert res.segment == "high"


def test_http_enrichment_400_no_retry() -> None:
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(400, json={"error": "Invalid format"})

    transport = httpx.MockTransport(handler)
    provider = HttpEnrichmentProvider(
        api_url="https://mock-enrichment.local/api/v1/enrich",
        transport=transport,
        backoff_delays=[0.01, 0.02, 0.03],
    )

    res = provider.enrich({"name": "Http User", "email": "user@http.com"})
    assert res.status == "failed"
    # Permanent client error must not be retried
    assert calls == 1


def test_http_enrichment_500_retries_3_times() -> None:
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(500, text="Internal Server Error")

    transport = httpx.MockTransport(handler)
    provider = HttpEnrichmentProvider(
        api_url="https://mock-enrichment.local/api/v1/enrich",
        transport=transport,
        backoff_delays=[0.01, 0.02, 0.03],
    )

    res = provider.enrich({"name": "Http User", "email": "user@http.com"})
    assert res.status == "failed"
    # Verify exactly 3 attempts took place
    assert calls == 3


def test_http_enrichment_timeout_handled_safely() -> None:
    calls = 0

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        raise httpx.ReadTimeout("Read timed out")

    transport = httpx.MockTransport(handler)
    provider = HttpEnrichmentProvider(
        api_url="https://mock-enrichment.local/api/v1/enrich",
        transport=transport,
        backoff_delays=[0.01, 0.02, 0.03],
    )

    res = provider.enrich({"name": "Http User", "email": "user@http.com"})
    assert res.status == "failed"
    assert "Timeout" in (res.error or "")
    assert calls == 3


def test_webhook_ingestion_succeeds_when_enrichment_fails(
    client: TestClient, db_session: Session, monkeypatch
) -> None:
    """Ensure that external enrichment failure does NOT crash lead creation."""
    def failing_enrich(self, lead_data):
        from app.services.enrichment import EnrichmentResult
        return EnrichmentResult(status="failed", error="Connection refused")

    monkeypatch.setattr(MockEnrichmentProvider, "enrich", failing_enrich)

    payload = {
        "name": "Resilient Lead",
        "email": "resilient@test.com",
        "source": "website",
    }
    response = client.post("/webhooks/leads", json=payload)
    assert response.status_code == 201
    lead_id = response.json()["lead_id"]

    # Verify lead was created with status 'failed'
    lead = db_session.get(Lead, lead_id)
    assert lead is not None
    assert lead.enrichment_status == "failed"
    assert lead.enrichment_score is None

    # Check enrichment_failed audit event was recorded
    events = db_session.execute(
        select(ProcessingEvent).where(ProcessingEvent.lead_id == lead_id)
    ).scalars().all()
    event_types = [e.event_type for e in events]
    assert "enrichment_failed" in event_types
