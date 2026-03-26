from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class User:
    """Represents a bot user stored in the database."""

    id: int
    telegram_id: int
    username: Optional[str]
    first_name: str
    last_name: Optional[str]
    created_at: datetime
    is_active: bool = True

    @classmethod
    def from_row(cls, row: dict) -> "User":
        """Create a User instance from a database row."""
        return cls(
            id=row["id"],
            telegram_id=row["telegram_id"],
            username=row["username"],
            first_name=row["first_name"],
            last_name=row["last_name"],
            created_at=datetime.fromisoformat(row["created_at"]),
            is_active=bool(row["is_active"]),
        )
