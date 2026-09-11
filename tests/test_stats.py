"""Tests for processing statistics endpoint."""

from fastapi.testclient import TestClient


def test_stats_counts_accurate(client: TestClient) -> None:
    # 1. Check initial empty stats
    res = client.get("/api/stats")
    assert res.status_code == 200
    stats = res.json()
    assert stats["total_leads"] == 0
    assert stats["total_webhooks_received"] == 0
    assert stats["created"] == 0
    assert stats["duplicates"] == 0
    assert stats["leads_by_source"] == {}

    # 2. Ingest valid lead A (shopify)
    client.post(
        "/webhooks/leads",
        json={"name": "Lead A", "email": "a@shop.com", "source": "shopify"},
    )

    # 3. Ingest duplicate of lead A
    client.post(
        "/webhooks/leads",
        json={"name": "Lead A", "email": "A@SHOP.COM", "source": "shopify"},
    )

    # 4. Ingest valid lead B (website)
    client.post(
        "/webhooks/leads",
        json={"name": "Lead B", "email": "b@web.com", "source": "website"},
    )

    res_updated = client.get("/api/stats")
    assert res_updated.status_code == 200
    data = res_updated.json()

    assert data["total_leads"] == 2
    assert data["total_webhooks_received"] == 3
    assert data["created"] == 2
    assert data["duplicates"] == 1
    assert data["leads_by_source"] == {"shopify": 1, "website": 1}
    # In mock mode, enrichment should be successful for both created leads
    assert data["enrichment_success"] == 2
    assert data["enrichment_failed"] == 0
