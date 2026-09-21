from fastapi import status
from fastapi.testclient import TestClient

from app.core.config import settings


def test_health_check_endpoint(client: TestClient) -> None:
    """Test GET /api/v1/health returns 200 OK and expected JSON structure."""
    response = client.get("/api/v1/health")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        "status": "ok",
        "service": settings.APP_NAME,
    }
