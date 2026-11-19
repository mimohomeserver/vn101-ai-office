from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "VN101 AI Office"
    app_env: str = "development"
    api_prefix: str = "/api/v1"
    mongodb_uri: str = ""
    mongodb_database: str = "vn101_ai_office"
    mongodb_server_selection_timeout_ms: int = 3000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
