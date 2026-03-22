"""Service layer for user operations."""

import logging
from typing import Optional

import aiosqlite

from bot.models.database import get_connection
from bot.models.user import User

logger = logging.getLogger(__name__)


class UserService:
    """Handles all user-related database operations."""

    def __init__(self, db_path: str) -> None:
        self._db_path = db_path

    async def _get_conn(self) -> aiosqlite.Connection:
        return await get_connection(self._db_path)

    async def get_or_create(
        self,
        telegram_id: int,
        username: Optional[str],
        first_name: str,
        last_name: Optional[str],
    ) -> User:
        """Retrieve an existing user or create a new one.

        Args:
            telegram_id: Telegram user ID.
            username: Telegram username (may be None).
            first_name: User's first name.
            last_name: User's last name (may be None).

        Returns:
            The User object.
        """
        conn = await self._get_conn()
        try:
            cursor = await conn.execute(
                "SELECT * FROM users WHERE telegram_id = ?", (telegram_id,)
            )
            row = await cursor.fetchone()
            if row:
                logger.debug("Found existing user: telegram_id=%d", telegram_id)
                return User.from_row(dict(row))

            await conn.execute(
                """INSERT INTO users (telegram_id, username, first_name, last_name)
                   VALUES (?, ?, ?, ?)""",
                (telegram_id, username, first_name, last_name),
            )
            await conn.commit()

            cursor = await conn.execute(
                "SELECT * FROM users WHERE telegram_id = ?", (telegram_id,)
            )
            row = await cursor.fetchone()
            logger.info("Created new user: telegram_id=%d", telegram_id)
            return User.from_row(dict(row))
        finally:
            await conn.close()

    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Find a user by their Telegram ID."""
        conn = await self._get_conn()
        try:
            cursor = await conn.execute(
                "SELECT * FROM users WHERE telegram_id = ?", (telegram_id,)
            )
            row = await cursor.fetchone()
            return User.from_row(dict(row)) if row else None
        finally:
            await conn.close()

    async def get_user_stats(self, user_id: int) -> dict:
        """Return task statistics for a given user."""
        conn = await self._get_conn()
        try:
            cursor = await conn.execute(
                """SELECT
                       COUNT(*) as total,
                       SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
                       SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending,
                       SUM(CASE WHEN status = 'in_progress' THEN 1 ELSE 0 END) as in_progress
                   FROM tasks WHERE user_id = ?""",
                (user_id,),
            )
            row = await cursor.fetchone()
            return dict(row) if row else {"total": 0, "completed": 0, "pending": 0, "in_progress": 0}
        finally:
            await conn.close()
