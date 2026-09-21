from datetime import datetime
from typing import Any, Dict, List, Optional
import uuid
from pydantic import BaseModel, ConfigDict, Field


class DocumentSearchRequest(BaseModel):
    """Request payload for semantic document search."""
    query: str = Field(..., min_length=1, max_length=1000, description="Natural language search query")
    top_k: Optional[int] = Field(None, ge=1, le=100, description="Maximum number of chunks to return")
    similarity_threshold: Optional[float] = Field(None, ge=0.0, le=1.0, description="Minimum cosine similarity score")
    document_id: Optional[uuid.UUID] = Field(None, description="Optional document filter")


class DocumentChunkResult(BaseModel):
    """Individual retrieved document chunk with source evidence."""
    chunk_id: uuid.UUID
    document_id: uuid.UUID
    chunk_index: int
    content: str
    score: float = Field(..., description="Cosine similarity score (0.0 to 1.0)")
    metadata: Optional[Dict[str, Any]] = None


class DocumentSearchResponse(BaseModel):
    """Structured response containing retrieved evidence for future AI agent reasoning."""
    query: str
    total_results: int
    results: List[DocumentChunkResult]
