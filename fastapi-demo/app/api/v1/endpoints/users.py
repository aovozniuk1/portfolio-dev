"""User API endpoints."""

from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.security import verify_api_key
from app.db.session import get_db
from app.schemas.common import PaginatedResponse
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"], dependencies=[Depends(verify_api_key)])


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(data: UserCreate, db: Session = Depends(get_db)) -> UserResponse:
    """Create a new user account."""
    service = UserService(db)
    user = service.create(data)
    return UserResponse.model_validate(user)


@router.get("/", response_model=PaginatedResponse[UserResponse])
def list_users(
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db),
) -> dict:
    """List users with pagination and optional filtering."""
    service = UserService(db)
    users, total = service.get_list(offset=offset, limit=limit, is_active=is_active)
    return {
        "items": [UserResponse.model_validate(u) for u in users],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)) -> UserResponse:
    """Get a single user by ID."""
    service = UserService(db)
    user = service.get_by_id(user_id)
    return UserResponse.model_validate(user)


@router.patch("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int, data: UserUpdate, db: Session = Depends(get_db)
) -> UserResponse:
    """Partially update a user."""
    service = UserService(db)
    user = service.update(user_id, data)
    return UserResponse.model_validate(user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)) -> None:
    """Delete a user and all their tasks."""
    service = UserService(db)
    service.delete(user_id)
