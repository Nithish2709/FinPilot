import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:
    """Repository handling database operations for the User entity."""

    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: uuid.UUID) -> Optional[User]:
        """Finds a user by UUID."""
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """Finds a user by email address (normalized to lowercase)."""
        normalized_email = email.strip().lower()
        stmt = select(User).where(User.email == normalized_email)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def create(
        db: AsyncSession,
        email: str,
        password_hash: str,
        name: str,
    ) -> User:
        """Creates a new user record in the database."""
        normalized_email = email.strip().lower()
        user = User(
            email=normalized_email,
            password_hash=password_hash,
            name=name.strip(),
            is_active=True,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
