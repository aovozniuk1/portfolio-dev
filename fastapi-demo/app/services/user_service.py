"""Business logic for user operations."""

from typing import List, Optional, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictException, NotFoundException
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class UserService:
    """Encapsulates user CRUD operations."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, data: UserCreate) -> User:
        """Create a new user.

        Raises:
            ConflictException: If the email or username already exists.
        """
        existing = (
            self.db.query(User)
            .filter((User.email == data.email) | (User.username == data.username))
            .first()
        )
        if existing:
            raise ConflictException("A user with this email or username already exists")

        user = User(email=data.email, username=data.username, full_name=data.full_name)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_by_id(self, user_id: int) -> User:
        """Retrieve a user by ID.

        Raises:
            NotFoundException: If no user with this ID exists.
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise NotFoundException("User", user_id)
        return user

    def get_list(
        self,
        offset: int = 0,
        limit: int = 20,
        is_active: Optional[bool] = None,
    ) -> Tuple[List[User], int]:
        """Return a paginated list of users with optional filtering.

        Returns:
            Tuple of (users list, total count).
        """
        query = self.db.query(User)
        if is_active is not None:
            query = query.filter(User.is_active == is_active)

        total = query.count()
        users = query.order_by(User.id).offset(offset).limit(limit).all()
        return users, total

    def update(self, user_id: int, data: UserUpdate) -> User:
        """Update a user's fields.

        Only non-None fields in the update schema are applied.
        """
        user = self.get_by_id(user_id)
        update_data = data.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(user, field, value)

        self.db.commit()
        self.db.refresh(user)
        return user

    def delete(self, user_id: int) -> None:
        """Delete a user and all associated tasks."""
        user = self.get_by_id(user_id)
        self.db.delete(user)
        self.db.commit()
