"""Application configuration."""

from pydantic_settings import BaseSettings


class AppConfig(BaseSettings):
    """Configuration loaded from environment / .env file."""

    openai_api_key: str = ""
    openai_model: str = "gpt-3.5-turbo"
    max_concurrent_requests: int = 5
    log_level: str = "INFO"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


config = AppConfig()
