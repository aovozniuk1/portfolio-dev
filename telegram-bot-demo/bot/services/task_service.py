"""Service layer for task operations."""

import logging
from datetime import UTC, datetime
from typing import List, Optional

import aiosqlite

from bot.models.database import get_connection
from bot.models.task import Task, TaskPriority, TaskStatus

logger = logging.getLogger(__name__)


class TaskService:
    """Handles all task-related database operations."""

    def __init__(self, db_path: str) -> None:
        self._db_path = db_path

    async def _get_conn(self) -> aiosqlite.Connection:
        return await get_connection(self._db_path)

    async def create(
        self,
        user_id: int,
        title: str,
        description: Optional[str] = None,
        priority: TaskPriority = TaskPriority.MEDIUM,
    ) -> Task:
        """Create a new task for the specified user.

        Args:
            user_id: Internal user ID (not Telegram ID).
            title: Short task title.
            description: Optional longer description.
            priority: Task priority level.

        Returns:
            The newly created Task.
        """
        conn = await self._get_conn()
        try:
            cursor = await conn.execute(
                """INSERT INTO tasks (user_id, title, description, priority)
                   VALUES (?, ?, ?, ?)""",
                (user_id, title, description, priority.value),
            )
            await conn.commit()
            task_id = cursor.lastrowid

            cursor = await conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
            row = await cursor.fetchone()
            logger.info("Created task #%d for user %d", task_id, user_id)
            return Task.from_row(dict(row))
        finally:
            await conn.close()

    async def get_by_user(
        self,
        user_id: int,
        status: Optional[TaskStatus] = None,
    ) -> List[Task]:
        """Retrieve all tasks for a user, optionally filtered by status.

        Args:
            user_id: Internal user ID.
            status: If provided, filter to this status only.

        Returns:
            List of matching Task objects.
        """
        conn = await self._get_conn()
        try:
            if status:
                cursor = await conn.execute(
                    "SELECT * FROM tasks WHERE user_id = ? AND status = ? ORDER BY created_at DESC",
                    (user_id, status.value),
                )
            else:
                cursor = await conn.execute(
                    "SELECT * FROM tasks WHERE user_id = ? ORDER BY created_at DESC",
                    (user_id,),
                )
            rows = await cursor.fetchall()
            return [Task.from_row(dict(r)) for r in rows]
        finally:
            await conn.close()

    async def get_by_id(self, task_id: int, user_id: int) -> Optional[Task]:
        """Find a single task by its ID, scoped to a user."""
        conn = await self._get_conn()
        try:
            cursor = await conn.execute(
                "SELECT * FROM tasks WHERE id = ? AND user_id = ?",
                (task_id, user_id),
            )
            row = await cursor.fetchone()
            return Task.from_row(dict(row)) if row else None
        finally:
            await conn.close()

    async def update_status(
        self, task_id: int, user_id: int, new_status: TaskStatus
    ) -> Optional[Task]:
        """Change the status of a task.

        Returns:
            The updated Task, or None if not found.
        """
        conn = await self._get_conn()
        try:
            now = datetime.now(UTC).isoformat()
            completed_at = now if new_status == TaskStatus.COMPLETED else None

            result = await conn.execute(
                """UPDATE tasks
                   SET status = ?, updated_at = ?, completed_at = COALESCE(?, completed_at)
                   WHERE id = ? AND user_id = ?""",
                (new_status.value, now, completed_at, task_id, user_id),
            )
            await conn.commit()

            if result.rowcount == 0:
                return None

            logger.info("Task #%d status changed to %s", task_id, new_status.value)
            return await self.get_by_id(task_id, user_id)
        finally:
            await conn.close()

    async def delete(self, task_id: int, user_id: int) -> bool:
        """Delete a task. Returns True if a row was removed."""
        conn = await self._get_conn()
        try:
            result = await conn.execute(
                "DELETE FROM tasks WHERE id = ? AND user_id = ?",
                (task_id, user_id),
            )
            await conn.commit()
            deleted = result.rowcount > 0
            if deleted:
                logger.info("Deleted task #%d for user %d", task_id, user_id)
            return deleted
        finally:
            await conn.close()
