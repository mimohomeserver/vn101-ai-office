from unittest.mock import AsyncMock, MagicMock

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


def test_readyz_returns_503_when_mongodb_is_not_configured() -> None:
    app.state.mongo_client = None
    response = client.get("/readyz")
    assert response.status_code == 503
    assert response.json()["detail"] == "MongoDB is not configured"


def test_readyz_returns_ready_when_mongodb_ping_succeeds() -> None:
    client_mock = MagicMock()
    client_mock.admin.command = AsyncMock(return_value={"ok": 1})
    app.state.mongo_client = client_mock
    response = client.get("/readyz")
    assert response.status_code == 200
    assert response.json() == {"status": "ready", "database": "connected"}


def test_readyz_returns_503_when_mongodb_ping_fails() -> None:
    client_mock = MagicMock()
    client_mock.admin.command = AsyncMock(side_effect=RuntimeError("connection failed"))
    app.state.mongo_client = client_mock
    response = client.get("/readyz")
    assert response.status_code == 503
    assert response.json()["detail"] == "MongoDB is unavailable"
