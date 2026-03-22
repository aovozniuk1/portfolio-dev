"""Shared response schemas."""

from typing import Generic, List, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response wrapper."""

    items: List[T]
    total: int
    limit: int
    offset: int


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str
