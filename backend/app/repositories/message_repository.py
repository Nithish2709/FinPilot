from typing import Any, Dict, List, Optional, Sequence, Tuple
import uuid
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.message import Message


class MessageRepository:
    """Handles message persistence and ordered retrieval."""

    @staticmethod
    async def get_next_sequence_number(db: AsyncSession, conversation_id: uuid.UUID) -> int:
        """Determines next sequence number for message ordering."""
        query = select(func.coalesce(func.max(Message.sequence_number), 0)).where(
            Message.conversation_id == conversation_id
        )
        result = await db.execute(query)
        max_seq = result.scalar() or 0
        return max_seq + 1

    @staticmethod
    async def create_message(
        db: AsyncSession,
        conversation_id: uuid.UUID,
        role: str,
        content: str,
        sequence_number: Optional[int] = None,
        model_used: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Message:
        if sequence_number is None:
            sequence_number = await MessageRepository.get_next_sequence_number(db, conversation_id)

        msg = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            sequence_number=sequence_number,
            model_used=model_used,
            metadata_=metadata,
        )
        db.add(msg)
        await db.commit()
        await db.refresh(msg)
        return msg

    @staticmethod
    async def get_messages_by_conversation(
        db: AsyncSession,
        conversation_id: uuid.UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[Sequence[Message], int]:
        base_query = select(Message).where(Message.conversation_id == conversation_id)

        count_query = select(func.count()).select_from(base_query.subquery())
        total = (await db.execute(count_query)).scalar() or 0

        # Ordered strictly ascending by sequence_number
        paged_query = (
            base_query.order_by(Message.sequence_number.asc())
            .limit(limit)
            .offset(offset)
        )
        items = (await db.execute(paged_query)).scalars().all()
        return items, total

    @staticmethod
    async def get_recent_messages(
        db: AsyncSession,
        conversation_id: uuid.UUID,
        limit: int = 20,
    ) -> List[Message]:
        """Fetches last N messages in chronological order."""
        query = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.sequence_number.desc())
            .limit(limit)
        )
        result = await db.execute(query)
        descending_msgs = result.scalars().all()
        # Reverse to chronological order (earliest first)
        return list(reversed(descending_msgs))

    @staticmethod
    async def count_messages(db: AsyncSession, conversation_id: uuid.UUID) -> int:
        query = select(func.count()).select_from(
            select(Message).where(Message.conversation_id == conversation_id).subquery()
        )
        result = await db.execute(query)
        return result.scalar() or 0
