from typing import Optional, Sequence
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.goal import Goal


class GoalRepository:
    """Handles goal database operations, strictly scoped to user_id."""

    @staticmethod
    async def create(db: AsyncSession, goal: Goal) -> Goal:
        db.add(goal)
        await db.commit()
        await db.refresh(goal)
        return goal

    @staticmethod
    async def get_by_id(db: AsyncSession, goal_id: uuid.UUID, user_id: uuid.UUID) -> Optional[Goal]:
        query = select(Goal).where(Goal.id == goal_id, Goal.user_id == user_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all_by_user(db: AsyncSession, user_id: uuid.UUID) -> Sequence[Goal]:
        query = select(Goal).where(Goal.user_id == user_id).order_by(Goal.created_at.desc())
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    async def update(db: AsyncSession, goal: Goal) -> Goal:
        await db.commit()
        await db.refresh(goal)
        return goal

    @staticmethod
    async def delete(db: AsyncSession, goal_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        goal = await GoalRepository.get_by_id(db, goal_id, user_id)
        if not goal:
            return False
        await db.delete(goal)
        await db.commit()
        return True
