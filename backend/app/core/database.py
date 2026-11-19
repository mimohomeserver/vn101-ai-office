from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase

from app.core.config import get_settings


def create_mongo_client() -> AsyncMongoClient | None:
    settings = get_settings()
    if not settings.mongodb_uri.strip():
        return None
    return AsyncMongoClient(
        settings.mongodb_uri,
        serverSelectionTimeoutMS=settings.mongodb_server_selection_timeout_ms,
    )


def get_mongo_database(client: AsyncMongoClient) -> AsyncDatabase:
    settings = get_settings()
    return client[settings.mongodb_database]
