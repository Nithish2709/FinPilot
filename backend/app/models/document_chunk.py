import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from sqlalchemy import DateTime, ForeignKey, Index, Integer, JSON, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import TypeDecorator

from app.core.config import settings
from app.core.database import Base

if TYPE_CHECKING:
    from app.models.document import Document
    from app.models.user import User


class VectorType(TypeDecorator):
    """
    Custom SQLAlchemy type for pgvector.
    On PostgreSQL with pgvector, renders as VECTOR(dim).
    Falls back gracefully to JSON on other dialects (such as SQLite in tests).
    """
    impl = JSON
    cache_ok = True

    def __init__(self, dim: Optional[int] = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dim = dim or settings.EMBEDDING_DIMENSION

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            try:
                from pgvector.sqlalchemy import Vector
                return dialect.type_descriptor(Vector(self.dim))
            except ImportError:
                return dialect.type_descriptor(JSONB())
        return dialect.type_descriptor(JSON())

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, (list, tuple)):
            return [float(x) for x in value]
        return value

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, (list, tuple)):
            return [float(x) for x in value]
        if hasattr(value, "tolist"):
            return value.tolist()
        return value


class DocumentChunk(Base):
    """SQLAlchemy model representing a chunk of a document with its vector embedding."""

    __tablename__ = "document_chunks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    chunk_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    embedding: Mapped[Optional[List[float]]] = mapped_column(
        VectorType(dim=settings.EMBEDDING_DIMENSION),
        nullable=True,
    )
    metadata_: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        "metadata",
        JSON().with_variant(JSONB, "postgresql"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    document: Mapped["Document"] = relationship("Document", back_populates="chunks")
    user: Mapped["User"] = relationship("User")

    __table_args__ = (
        Index("ix_document_chunks_user_id", "user_id"),
        Index("ix_document_chunks_document_id", "document_id"),
        Index("ix_document_chunks_doc_chunk_idx", "document_id", "chunk_index"),
    )

