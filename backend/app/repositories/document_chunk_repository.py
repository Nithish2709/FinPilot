import math
from typing import Any, Dict, List, Optional, Sequence, Tuple
import uuid
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document_chunk import DocumentChunk


class DocumentChunkRepository:
    """Repository handling persistence, deletion, and user-scoped semantic retrieval of chunks."""

    @staticmethod
    async def delete_by_document_id(db: AsyncSession, document_id: uuid.UUID) -> int:
        """Deletes all chunks belonging to a document (for idempotent reprocessing)."""
        stmt = delete(DocumentChunk).where(DocumentChunk.document_id == document_id)
        res = await db.execute(stmt)
        await db.commit()
        return res.rowcount or 0

    @staticmethod
    async def bulk_create_chunks(
        db: AsyncSession,
        chunks_data: List[Dict[str, Any]],
    ) -> List[DocumentChunk]:
        """Bulk inserts document chunks."""
        if not chunks_data:
            return []

        chunks = [DocumentChunk(**data) for data in chunks_data]
        db.add_all(chunks)
        await db.commit()
        for c in chunks:
            await db.refresh(c)
        return chunks

    @staticmethod
    async def get_by_document_id(
        db: AsyncSession,
        document_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> Sequence[DocumentChunk]:
        """Retrieves chunks strictly scoped to the owning user."""
        query = (
            select(DocumentChunk)
            .where(
                DocumentChunk.document_id == document_id,
                DocumentChunk.user_id == user_id,
            )
            .order_by(DocumentChunk.chunk_index.asc())
        )
        result = await db.execute(query)
        return result.scalars().all()

    @staticmethod
    def _cosine_similarity(vec1: Sequence[float], vec2: Sequence[float]) -> float:
        """Computes cosine similarity between two vector sequences."""
        if not vec1 or not vec2 or len(vec1) != len(vec2):
            return 0.0
        dot = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))
        if norm1 < 1e-9 or norm2 < 1e-9:
            return 0.0
        # Cosine similarity bounded in [-1.0, 1.0] -> normalize or clamp [0.0, 1.0]
        score = dot / (norm1 * norm2)
        return max(0.0, min(1.0, (score + 1.0) / 2.0)) if score < 0 else min(1.0, score)

    @classmethod
    async def search_similar_chunks(
        cls,
        db: AsyncSession,
        user_id: uuid.UUID,
        query_vector: List[float],
        top_k: int = 5,
        similarity_threshold: float = 0.5,
        document_id: Optional[uuid.UUID] = None,
    ) -> List[Tuple[DocumentChunk, float]]:
        """
        User-isolated semantic vector retrieval.
        CRITICAL: Strictly filters by authenticated user_id.
        Works across PostgreSQL + pgvector as well as SQLite in-memory tests.
        """
        stmt = select(DocumentChunk).where(DocumentChunk.user_id == user_id)
        if document_id is not None:
            stmt = stmt.where(DocumentChunk.document_id == document_id)

        # Check dialect
        bind = db.bind
        dialect_name = bind.dialect.name if bind else "postgresql"

        if dialect_name == "postgresql":
            # Native PostgreSQL pgvector cosine distance operator (<=>)
            try:
                # 1 - (embedding <=> query_vector) = cosine similarity
                distance_expr = DocumentChunk.embedding.cosine_distance(query_vector)
                sim_expr = (1.0 - distance_expr).label("similarity")
                pg_stmt = (
                    select(DocumentChunk, sim_expr)
                    .where(DocumentChunk.user_id == user_id)
                )
                if document_id is not None:
                    pg_stmt = pg_stmt.where(DocumentChunk.document_id == document_id)

                pg_stmt = (
                    pg_stmt.where(sim_expr >= similarity_threshold)
                    .order_by(distance_expr.asc())
                    .limit(top_k)
                )
                res = await db.execute(pg_stmt)
                return [(row[0], float(row[1])) for row in res.all()]
            except Exception:
                # Fallback to in-memory score computation if dialect function not registered
                pass

        # Universal fallback (evaluates vectors and sorts by cosine similarity)
        res = await db.execute(stmt)
        all_chunks = res.scalars().all()

        scored_chunks: List[Tuple[DocumentChunk, float]] = []
        for chunk in all_chunks:
            if chunk.embedding:
                score = cls._cosine_similarity(query_vector, chunk.embedding)
                if score >= similarity_threshold:
                    scored_chunks.append((chunk, score))

        # Sort descending by score
        scored_chunks.sort(key=lambda x: x[1], reverse=True)
        return scored_chunks[:top_k]
