"""Pydantic v2 schemas for Task endpoints."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

from app.models.task import TaskPriority, TaskStatus


class TaskCreate(BaseModel):
    """Schema for creating a new task."""

    title: str = Field(..., min_length=1, max_length=300, examples=["Implement login page"])
    description: Optional[str] = Field(None, examples=["Build the login form with validation"])
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM)
    owner_id: int = Field(..., gt=0)


class TaskUpdate(BaseModel):
    """Schema for partially updating a task."""

    title: Optional[str] = Field(None, min_length=1, max_length=300)
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None


class TaskResponse(BaseModel):
    """Schema for task responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: Optional[str]
    status: TaskStatus
    priority: TaskPriority
    owner_id: int
    created_at: datetime
    updated_at: datetime
