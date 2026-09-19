from datetime import datetime
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, ConfigDict, Field


# -------------------------------------------------------------
# Conversation Schemas
# -------------------------------------------------------------

class ConversationCreate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)


class ConversationUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    archived: Optional[bool] = None


class ConversationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    title: Optional[str] = None
    archived: bool
    created_at: datetime
    updated_at: datetime


class ConversationListResponse(BaseModel):
    items: List[ConversationResponse]
    total: int
    limit: int
    offset: int


# -------------------------------------------------------------
# Message Schemas
# -------------------------------------------------------------

class MessageCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=16000)


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    conversation_id: uuid.UUID
    role: str
    content: str
    sequence_number: int
    model_used: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = Field(None, alias="metadata_")
    created_at: datetime


class MessageListResponse(BaseModel):
    items: List[MessageResponse]
    total: int
    limit: int
    offset: int


# -------------------------------------------------------------
# Summary & Context Schemas
# -------------------------------------------------------------

class ConversationSummaryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    conversation_id: uuid.UUID
    summary: str
    message_count: int
    updated_at: datetime


class ContextMessageItem(BaseModel):
    role: str
    content: str
    sequence_number: int


class ConversationContextResponse(BaseModel):
    conversation_id: uuid.UUID
    summary: Optional[str] = None
    recent_messages: List[ContextMessageItem]
    message_count: int
