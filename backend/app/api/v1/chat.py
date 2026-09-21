from typing import Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
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
from app.services.chat_service import ChatService

router = APIRouter(prefix="/conversations", tags=["Chat & Conversations"])


# -------------------------------------------------------------
# Conversation Endpoints
# -------------------------------------------------------------

@router.post(
    "",
    response_model=ConversationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new conversation",
)
async def create_conversation(
    data: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ConversationResponse:
    return await ChatService.create_conversation(db, user_id=current_user.id, data=data)


@router.get(
    "",
    response_model=ConversationListResponse,
    status_code=status.HTTP_200_OK,
    summary="List conversations for current user",
)
async def list_conversations(
    archived: Optional[bool] = Query(None, description="Filter by archived status"),
    limit: int = Query(50, ge=1, le=100, description="Page limit (max 100)"),
    offset: int = Query(0, ge=0, description="Page offset"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ConversationListResponse:
    return await ChatService.list_conversations(
        db, user_id=current_user.id, archived=archived, limit=limit, offset=offset
    )


@router.get(
    "/{conversation_id}",
    response_model=ConversationResponse,
    status_code=status.HTTP_200_OK,
    summary="Get conversation metadata by ID",
)
async def get_conversation(
    conversation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ConversationResponse:
    conv = await ChatService.get_conversation(db, conversation_id, user_id=current_user.id)
    if not conv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found or does not belong to authenticated user.",
        )
    return conv


@router.patch(
    "/{conversation_id}",
    response_model=ConversationResponse,
    status_code=status.HTTP_200_OK,
    summary="Update conversation title or archive status",
)
async def update_conversation(
    conversation_id: uuid.UUID,
    data: ConversationUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ConversationResponse:
    updated = await ChatService.update_conversation(db, conversation_id, current_user.id, data)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found or does not belong to authenticated user.",
        )
    return updated


@router.delete(
    "/{conversation_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete conversation and cascade its messages and summary",
)
async def delete_conversation(
    conversation_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    deleted = await ChatService.delete_conversation(db, conversation_id, user_id=current_user.id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found or does not belong to authenticated user.",
        )
    return {"message": "Conversation deleted"}


# -------------------------------------------------------------
# Message Endpoints
# -------------------------------------------------------------

@router.get(
    "/{conversation_id}/messages",
    response_model=MessageListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get message history for conversation",
)
async def get_messages(
    conversation_id: uuid.UUID,
    limit: int = Query(50, ge=1, le=100, description="Page limit (max 100)"),
    offset: int = Query(0, ge=0, description="Page offset"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MessageListResponse:
    history = await ChatService.get_message_history(
        db, conversation_id, user_id=current_user.id, limit=limit, offset=offset
    )
    if not history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found or does not belong to authenticated user.",
        )
    return history


@router.post(
    "/{conversation_id}/messages",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Post a user message and receive placeholder assistant response",
)
async def post_message(
    conversation_id: uuid.UUID,
    data: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    result = await ChatService.add_user_message(
        db, conversation_id=conversation_id, user_id=current_user.id, data=data
    )
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found or does not belong to authenticated user.",
        )
    user_msg, asst_msg = result
    # Return placeholder assistant response
    return asst_msg


# -------------------------------------------------------------
# Context Endpoint (Internal/Debug Context inspection)
# -------------------------------------------------------------

@router.get(
    "/{conversation_id}/context",
    response_model=ConversationContextResponse,
    status_code=status.HTTP_200_OK,
    summary="Inspect assembled conversation context window for future AI ingestion",
)
async def get_context(
    conversation_id: uuid.UUID,
    limit: int = Query(20, ge=1, le=50, description="Context window message limit"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ConversationContextResponse:
    context = await ChatService.build_context(
        db, conversation_id=conversation_id, user_id=current_user.id, limit=limit
    )
    if not context:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found or does not belong to authenticated user.",
        )
    return context
