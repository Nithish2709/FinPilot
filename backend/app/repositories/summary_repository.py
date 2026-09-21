from datetime import datetime, timezone
from typing import Optional
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conversation_summary import ConversationSummary


class SummaryRepository:
    """Handles conversation summary persistence."""

    @staticmethod
    async def get_by_conversation_id(
        db: AsyncSession,
        conversation_id: uuid.UUID,
    ) -> Optional[ConversationSummary]:
        query = select(ConversationSummary).where(
            ConversationSummary.conversation_id == conversation_id
        )
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def upsert_summary(
        db: AsyncSession,
        conversation_id: uuid.UUID,
        summary: str,
        message_count: int,
    ) -> ConversationSummary:
        existing = await SummaryRepository.get_by_conversation_id(db, conversation_id)
        if existing:
            existing.summary = summary
            existing.message_count = message_count
            existing.updated_at = datetime.now(timezone.utc)
            await db.commit()
            await db.refresh(existing)
            return existing

        new_sum = ConversationSummary(
            conversation_id=conversation_id,
            summary=summary,
            message_count=message_count,
        )
        db.add(new_sum)
        await db.commit()
        await db.refresh(new_sum)
        return new_sum
