from typing import List, Optional, Tuple
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conversation import Conversation
from app.models.message import Message, MessageRole
from app.repositories.conversation_repository import ConversationRepository
from app.repositories.message_repository import MessageRepository
from app.repositories.summary_repository import SummaryRepository
from app.schemas.chat import (
    ConversationContextResponse,
    ConversationCreate,
    ConversationListResponse,
    ConversationResponse,
    ConversationUpdate,
    MessageCreate,
    MessageListResponse,
    MessageResponse,
)
from app.agent.agent_service import AgentService
from app.services.context_service import ContextService


class ChatService:
    """
    Orchestrates conversation lifecycle and message persistence.
    Operates independently of future AI agents.
    """

    PLACEHOLDER_ASSISTANT_CONTENT = (
        "Your financial assistant is being initialized. The AI agent will be connected in a later stage."
    )

    # ---------------------------------------------------------
    # Conversation Management
    # ---------------------------------------------------------
    @staticmethod
    async def create_conversation(
        db: AsyncSession,
        user_id: uuid.UUID,
        data: ConversationCreate,
    ) -> ConversationResponse:
        conv = Conversation(
            user_id=user_id,
            title=data.title,
            archived=False,
        )
        created = await ConversationRepository.create(db, conv)
        return ConversationResponse.model_validate(created)

    @staticmethod
    async def get_conversation(
        db: AsyncSession,
        conversation_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> Optional[ConversationResponse]:
        conv = await ConversationRepository.get_by_id_and_user(db, conversation_id, user_id)
        if not conv:
            return None
        return ConversationResponse.model_validate(conv)

    @staticmethod
    async def list_conversations(
        db: AsyncSession,
        user_id: uuid.UUID,
        archived: Optional[bool] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> ConversationListResponse:
        items, total = await ConversationRepository.list_by_user(
            db, user_id=user_id, archived=archived, limit=limit, offset=offset
        )
        return ConversationListResponse(
            items=[ConversationResponse.model_validate(c) for c in items],
            total=total,
            limit=limit,
            offset=offset,
        )

    @staticmethod
    async def update_conversation(
        db: AsyncSession,
        conversation_id: uuid.UUID,
        user_id: uuid.UUID,
        data: ConversationUpdate,
    ) -> Optional[ConversationResponse]:
        conv = await ConversationRepository.get_by_id_and_user(db, conversation_id, user_id)
        if not conv:
            return None

        if data.title is not None:
            conv.title = data.title
        if data.archived is not None:
            conv.archived = data.archived

        updated = await ConversationRepository.update(db, conv)
        return ConversationResponse.model_validate(updated)

    @staticmethod
    async def delete_conversation(
        db: AsyncSession,
        conversation_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> bool:
        conv = await ConversationRepository.get_by_id_and_user(db, conversation_id, user_id)
        if not conv:
            return False
        await ConversationRepository.delete(db, conv)
        return True

    # ---------------------------------------------------------
    # Message Handling & History
    # ---------------------------------------------------------
    @classmethod
    async def add_user_message(
        cls,
        db: AsyncSession,
        conversation_id: uuid.UUID,
        user_id: uuid.UUID,
        data: MessageCreate,
    ) -> Optional[Tuple[MessageResponse, MessageResponse]]:
        """
        Persists a USER message and immediately appends a placeholder ASSISTANT response.
        Updates conversation.updated_at.
        Returns: (user_message_response, assistant_message_response)
        """
        # Strictly verify conversation belongs to authenticated user
        conv = await ConversationRepository.get_by_id_and_user(db, conversation_id, user_id)
        if not conv:
            return None

        # 1. Allocate sequence number for USER message
        user_seq = await MessageRepository.get_next_sequence_number(db, conversation_id)
        user_msg = await MessageRepository.create_message(
            db=db,
            conversation_id=conversation_id,
            role=MessageRole.USER.value,
            content=data.content,
            sequence_number=user_seq,
        )

        # 2. Run local Qwen tool-calling agent loop
        agent_svc = AgentService()
        try:
            agent_result = await agent_svc.process_message(
                db=db,
                user_id=user_id,
                conversation_id=conversation_id,
                user_message=data.content,
            )
            asst_content = agent_result["answer"]
            model_identifier = agent_result["model_used"]
            msg_metadata = agent_result.get("metadata")
        except Exception as e:
            asst_content = "I encountered an error retrieving your financial data. Please try again."
            model_identifier = f"local:{cls.PLACEHOLDER_ASSISTANT_CONTENT[:5]}"
            msg_metadata = {"error": str(e)}

        # 3. Allocate next sequence number for persistent ASSISTANT message
        asst_seq = user_seq + 1
        asst_msg = await MessageRepository.create_message(
            db=db,
            conversation_id=conversation_id,
            role=MessageRole.ASSISTANT.value,
            content=asst_content,
            sequence_number=asst_seq,
            model_used=model_identifier,
            metadata=msg_metadata,
        )

        # 4. Touch conversation updated_at
        await ConversationRepository.touch_updated_at(db, conversation_id)

        return (
            MessageResponse.model_validate(user_msg),
            MessageResponse.model_validate(asst_msg),
        )

    @staticmethod
    async def get_message_history(
        db: AsyncSession,
        conversation_id: uuid.UUID,
        user_id: uuid.UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> Optional[MessageListResponse]:
        # Enforce user ownership
        conv = await ConversationRepository.get_by_id_and_user(db, conversation_id, user_id)
        if not conv:
            return None

        items, total = await MessageRepository.get_messages_by_conversation(
            db, conversation_id=conversation_id, limit=limit, offset=offset
        )
        return MessageListResponse(
            items=[MessageResponse.model_validate(m) for m in items],
            total=total,
            limit=limit,
            offset=offset,
        )

    @staticmethod
    async def build_context(
        db: AsyncSession,
        conversation_id: uuid.UUID,
        user_id: uuid.UUID,
        limit: Optional[int] = None,
    ) -> Optional[ConversationContextResponse]:
        return await ContextService.build_conversation_context(
            db, conversation_id, user_id, limit=limit
        )
