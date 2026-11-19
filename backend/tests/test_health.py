from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_healthz_returns_ok() -> None:
    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["service"] == "vn101-ai-office-api"


def test_root_returns_service_information() -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["name"] == "VN101 AI Office"
