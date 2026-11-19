from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from app.core.auth import get_current_user
from app.main import app


class FakeUsers:
    def __init__(self) -> None:
        self.update_one = AsyncMock()
        self.find_one = AsyncMock(
            return_value={
                "firebase_uid": "firebase-user-123",
                "email": "member@example.com",
                "display_name": "Member",
                "photo_url": None,
                "email_verified": True,
                "role": "user",
            }
        )


class FakeDatabase:
    def __init__(self, users: FakeUsers) -> None:
        self.users = users

    def __getitem__(self, name: str) -> FakeUsers:
        assert name == "users"
        return self.users


class FakeMongoClient:
    def __init__(self, users: FakeUsers) -> None:
        self.database = FakeDatabase(users)

    def __getitem__(self, name: str) -> FakeDatabase:
        assert name == "vn101_ai_office"
        return self.database


def test_me_requires_authentication() -> None:
    response = TestClient(app).get("/api/v1/users/me")
    assert response.status_code == 401


def test_me_creates_default_user_profile() -> None:
    users = FakeUsers()
    app.state.mongo_client = FakeMongoClient(users)
    app.dependency_overrides[get_current_user] = lambda: {
        "uid": "firebase-user-123",
        "email": "member@example.com",
        "name": "Member",
        "email_verified": True,
    }
    try:
        response = TestClient(app).get("/api/v1/users/me")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["role"] == "user"
    update = users.update_one.await_args.args[1]
    assert update["$setOnInsert"]["role"] == "user"
    assert "role" not in update["$set"]


def test_me_returns_503_without_mongodb() -> None:
    app.state.mongo_client = None
    app.dependency_overrides[get_current_user] = lambda: {
        "uid": "firebase-user-123",
        "email_verified": True,
    }
    try:
        response = TestClient(app).get("/api/v1/users/me")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 503
