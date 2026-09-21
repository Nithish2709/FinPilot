import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class TransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    account_id: Optional[uuid.UUID] = None
    source_document_id: Optional[uuid.UUID] = None
    transaction_date: date
    merchant: Optional[str] = None
    description: str
    amount: Decimal
    currency: str
    transaction_type: str
    category: Optional[str] = None
    subcategory: Optional[str] = None
    is_recurring: bool = False
    confidence: Optional[Decimal] = None
    external_reference: Optional[str] = None
    is_duplicate: bool = False
    is_valid: bool = True
    validation_error: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class TransactionListResponse(BaseModel):
    items: List[TransactionResponse]
    total: int
    limit: int
    offset: int
