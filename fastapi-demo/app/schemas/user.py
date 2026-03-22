"""Pydantic v2 schemas for User endpoints."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserCreate(BaseModel):
    """Schema for creating a new user."""

    email: str = Field(..., max_length=255, examples=["john@example.com"])
    username: str = Field(..., min_length=3, max_length=100, examples=["johndoe"])
    full_name: str = Field(..., min_length=1, max_length=200, examples=["John Doe"])


class UserUpdate(BaseModel):
    """Schema for partially updating a user."""

    email: Optional[str] = Field(None, max_length=255)
    username: Optional[str] = Field(None, min_length=3, max_length=100)
    full_name: Optional[str] = Field(None, min_length=1, max_length=200)
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    """Schema for user responses."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    username: str
    full_name: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
