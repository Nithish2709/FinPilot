from typing import Optional
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.message_repository import MessageRepository
from app.repositories.summary_repository import SummaryRepository
from app.schemas.chat import ContextMessageItem, ConversationContextResponse


class ContextService:
    """
    Context builder abstraction for future AI/LLM consumption.
    Selects the conversation summary and the last N (default 20) recent messages
    in chronological order, preventing token blowout while preserving full DB history.
    """

    DEFAULT_CONTEXT_MESSAGE_LIMIT = settings.CHAT_CONTEXT_MESSAGE_LIMIT

    @classmethod
    async def build_conversation_context(
        cls,
        db: AsyncSession,
        conversation_id: uuid.UUID,
        user_id: uuid.UUID,
        limit: Optional[int] = None,
    ) -> Optional[ConversationContextResponse]:
        # Enforce user ownership first
        conv = await ConversationRepository.get_by_id_and_user(db, conversation_id, user_id)
        if not conv:
            return None

        msg_limit = limit or cls.DEFAULT_CONTEXT_MESSAGE_LIMIT

        # 1. Retrieve summary if one exists
        summary_record = await SummaryRepository.get_by_conversation_id(db, conversation_id)
        summary_text = summary_record.summary if summary_record else None

        # 2. Retrieve recent messages (chronological order)
        recent_msgs = await MessageRepository.get_recent_messages(db, conversation_id, limit=msg_limit)
        context_items = [
            ContextMessageItem(
                role=m.role,
                content=m.content,
                sequence_number=m.sequence_number,
            )
            for m in recent_msgs
        ]

        # 3. Total message count
        total_count = await MessageRepository.count_messages(db, conversation_id)

        return ConversationContextResponse(
            conversation_id=conversation_id,
            summary=summary_text,
            recent_messages=context_items,
            message_count=total_count,
        )
