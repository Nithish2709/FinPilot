from typing import Optional, Sequence
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document


class DocumentRepository:
    """Handles database queries for documents, strictly scoped to the authenticated user."""

    @staticmethod
    async def create(db: AsyncSession, document: Document) -> Document:
        db.add(document)
        await db.commit()
        await db.refresh(document)
        return document

    @staticmethod
    async def get_by_id_and_user(
        db: AsyncSession,
        document_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> Optional[Document]:
        """Ensures document is retrieved strictly by document_id AND user_id."""
        query = select(Document).where(Document.id == document_id, Document.user_id == user_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def update(db: AsyncSession, document: Document) -> Document:
        await db.commit()
        await db.refresh(document)
        return document

    @staticmethod
    async def get_all_by_user(
        db: AsyncSession,
        user_id: uuid.UUID,
        limit: int = 50,
        offset: int = 0,
    ) -> Sequence[Document]:
        query = (
            select(Document)
            .where(Document.user_id == user_id)
            .order_by(Document.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await db.execute(query)
        return result.scalars().all()
