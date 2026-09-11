"""Tests for lead query and retrieval endpoints."""

from fastapi.testclient import TestClient


def test_get_leads_empty(client: TestClient) -> None:
    response = client.get("/api/leads")
    assert response.status_code == 200
    data = response.json()
    assert data["page"] == 1
    assert data["page_size"] == 50
    assert data["total"] == 0
    assert data["items"] == []


def test_get_leads_pagination_and_filter(client: TestClient) -> None:
    # Ingest 3 leads across different sources
    leads_to_create = [
        {"name": "User 1", "email": "user1@site.com", "source": "shopify"},
        {"name": "User 2", "email": "user2@site.com", "source": "shopify"},
        {"name": "User 3", "email": "user3@site.com", "source": "facebook"},
    ]
    for lead in leads_to_create:
        res = client.post("/webhooks/leads", json=lead)
        assert res.status_code == 201

    # Test all leads
    res = client.get("/api/leads?page=1&page_size=2")
    data = res.json()
    assert data["total"] == 3
    assert len(data["items"]) == 2

    # Test source filter
    res_filtered = client.get("/api/leads?source=shopify")
    data_filtered = res_filtered.json()
    assert data_filtered["total"] == 2
    for item in data_filtered["items"]:
        assert item["source"] == "shopify"


def test_get_single_lead_success(client: TestClient) -> None:
    res = client.post(
        "/webhooks/leads",
        json={"name": "Alice Lead", "email": "alice@lead.com", "company": "Tech Corp"},
    )
    assert res.status_code == 201
    lead_id = res.json()["lead_id"]

    res_single = client.get(f"/api/leads/{lead_id}")
    assert res_single.status_code == 200
    data = res_single.json()
    assert data["id"] == lead_id
    assert data["name"] == "Alice Lead"
    assert data["email"] == "alice@lead.com"
    assert data["company"] == "Tech Corp"


def test_get_single_lead_not_found(client: TestClient) -> None:
    response = client.get("/api/leads/99999")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()
