import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class DocumentBase(BaseModel):
    filename: str
    status: str
    mime_type: Optional[str] = None
    file_size: Optional[int] = None


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    document_id: uuid.UUID
    filename: str
    status: str
    total_records: int = 0
    successful_records: int = 0
    failed_records: int = 0
    duplicate_records: int = 0
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None


class DocumentDetailResponse(DocumentResponse):
    mime_type: Optional[str] = None
    file_size: Optional[int] = None
    storage_key: Optional[str] = None
    updated_at: Optional[datetime] = None


class ImportSummaryResponse(BaseModel):
    document_id: uuid.UUID
    filename: str
    status: str
    total_records: int
    successful_records: int
    failed_records: int
    duplicate_records: int
    error_message: Optional[str] = None
