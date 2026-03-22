"""Application configuration loaded from environment variables."""

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Config:
    """Bot configuration container."""

    bot_token: str = field(default_factory=lambda: os.getenv("BOT_TOKEN", ""))
    database_path: str = field(
        default_factory=lambda: os.getenv("DATABASE_PATH", "data/bot.db")
    )
    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))

    def __post_init__(self) -> None:
        if not self.bot_token:
            raise ValueError("BOT_TOKEN environment variable is required")
        db_dir = Path(self.database_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)


def get_config() -> Config:
    """Create and return a validated configuration instance."""
    return Config()
