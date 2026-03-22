"""Task API endpoints."""

from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.security import verify_api_key
from app.db.session import get_db
from app.models.task import TaskPriority, TaskStatus
from app.schemas.common import PaginatedResponse
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate
from app.services.task_service import TaskService

router = APIRouter(prefix="/tasks", tags=["Tasks"], dependencies=[Depends(verify_api_key)])


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(data: TaskCreate, db: Session = Depends(get_db)) -> TaskResponse:
    """Create a new task for a user."""
    service = TaskService(db)
    task = service.create(data)
    return TaskResponse.model_validate(task)


@router.get("/", response_model=PaginatedResponse[TaskResponse])
def list_tasks(
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status_filter: Optional[TaskStatus] = Query(None, alias="status"),
    priority: Optional[TaskPriority] = Query(None),
    owner_id: Optional[int] = Query(None),
    sort_by: str = Query("created_at", pattern="^(created_at|updated_at|title|priority)$"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db),
) -> dict:
    """List tasks with pagination, filtering, and sorting."""
    service = TaskService(db)
    tasks, total = service.get_list(
        offset=offset,
        limit=limit,
        status=status_filter,
        priority=priority,
        owner_id=owner_id,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    return {
        "items": [TaskResponse.model_validate(t) for t in tasks],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)) -> TaskResponse:
    """Get a single task by ID."""
    service = TaskService(db)
    task = service.get_by_id(task_id)
    return TaskResponse.model_validate(task)


@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int, data: TaskUpdate, db: Session = Depends(get_db)
) -> TaskResponse:
    """Partially update a task."""
    service = TaskService(db)
    task = service.update(task_id, data)
    return TaskResponse.model_validate(task)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db)) -> None:
    """Delete a task by ID."""
    service = TaskService(db)
    service.delete(task_id)
