"""Business logic for task operations."""

from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundException
from app.models.task import Task, TaskPriority, TaskStatus
from app.schemas.task import TaskCreate, TaskUpdate


class TaskService:
    """Encapsulates task CRUD operations."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, data: TaskCreate) -> Task:
        """Create a new task linked to an existing user."""
        from app.models.user import User

        owner = self.db.query(User).filter(User.id == data.owner_id).first()
        if not owner:
            raise NotFoundException("User", data.owner_id)

        task = Task(
            title=data.title,
            description=data.description,
            priority=data.priority,
            owner_id=data.owner_id,
        )
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def get_by_id(self, task_id: int) -> Task:
        """Retrieve a task by ID.

        Raises:
            NotFoundException: If no task with this ID exists.
        """
        task = self.db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise NotFoundException("Task", task_id)
        return task

    def get_list(
        self,
        offset: int = 0,
        limit: int = 20,
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None,
        owner_id: Optional[int] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> Tuple[List[Task], int]:
        """Return a paginated, filterable, sortable list of tasks.

        Args:
            offset: Number of records to skip.
            limit: Maximum number of records to return.
            status: Filter by task status.
            priority: Filter by priority level.
            owner_id: Filter by owning user.
            sort_by: Column name to sort on.
            sort_order: 'asc' or 'desc'.

        Returns:
            Tuple of (tasks list, total count).
        """
        query = self.db.query(Task)

        if status:
            query = query.filter(Task.status == status)
        if priority:
            query = query.filter(Task.priority == priority)
        if owner_id:
            query = query.filter(Task.owner_id == owner_id)

        total = query.count()

        sort_column = getattr(Task, sort_by, Task.created_at)
        if sort_order == "asc":
            query = query.order_by(sort_column.asc())
        else:
            query = query.order_by(sort_column.desc())

        tasks = query.offset(offset).limit(limit).all()
        return tasks, total

    def update(self, task_id: int, data: TaskUpdate) -> Task:
        """Update a task's fields."""
        task = self.get_by_id(task_id)
        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(task, field, value)

        self.db.commit()
        self.db.refresh(task)
        return task

    def delete(self, task_id: int) -> None:
        """Delete a task by ID."""
        task = self.get_by_id(task_id)
        self.db.delete(task)
        self.db.commit()
