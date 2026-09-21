from datetime import datetime, timezone
from typing import Optional, Sequence, Tuple
import uuid
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conversation import Conversation


class ConversationRepository:
    """Handles conversation persistence and retrieval, strictly user-scoped."""

    @staticmethod
    async def create(db: AsyncSession, conversation: Conversation) -> Conversation:
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)
        return conversation

    @staticmethod
    async def get_by_id_and_user(
        db: AsyncSession,
        conversation_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> Optional[Conversation]:
        query = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id,
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def list_by_user(
        db: AsyncSession,
        user_id: uuid.UUID,
        archived: Optional[bool] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[Sequence[Conversation], int]:
        base_query = select(Conversation).where(Conversation.user_id == user_id)
        if archived is not None:
            base_query = base_query.where(Conversation.archived == archived)

        count_query = select(func.count()).select_from(base_query.subquery())
        total = (await db.execute(count_query)).scalar() or 0

        paged_query = (
            base_query.order_by(Conversation.updated_at.desc())
            .limit(limit)
            .offset(offset)
        )
        items = (await db.execute(paged_query)).scalars().all()
        return items, total

    @staticmethod
    async def update(db: AsyncSession, conversation: Conversation) -> Conversation:
        conversation.updated_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(conversation)
        return conversation

    @staticmethod
    async def touch_updated_at(db: AsyncSession, conversation_id: uuid.UUID) -> None:
        """Updates updated_at timestamp when a new message is added."""
        query = select(Conversation).where(Conversation.id == conversation_id)
        result = await db.execute(query)
        conv = result.scalar_one_or_none()
        if conv:
            conv.updated_at = datetime.now(timezone.utc)
            await db.commit()

    @staticmethod
    async def delete(db: AsyncSession, conversation: Conversation) -> None:
        await db.delete(conversation)
        await db.commit()
