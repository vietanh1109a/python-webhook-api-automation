"""Tests for the health check endpoint."""

from fastapi.testclient import TestClient


def test_health_check_returns_200(client: TestClient) -> None:
    """Verify that GET /health returns HTTP 200 and status ok."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
