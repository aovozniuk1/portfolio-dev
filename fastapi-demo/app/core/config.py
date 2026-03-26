"""Application configuration via pydantic-settings."""

from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Central configuration loaded from environment / .env file."""

    database_url: str = "sqlite:///./app.db"
    secret_key: str = "change-me-to-a-random-secret"
    api_key: str = "dev-api-key-change-in-production"
    access_token_expire_minutes: int = 60
    app_name: str = "Task Management API"
    allowed_origins: List[str] = ["http://localhost:3000"]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
