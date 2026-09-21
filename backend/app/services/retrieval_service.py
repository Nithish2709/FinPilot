from typing import List, Optional
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.repositories.document_chunk_repository import DocumentChunkRepository
from app.schemas.retrieval import DocumentChunkResult, DocumentSearchResponse
from app.services.embeddings.local import get_embedding_provider


class RetrievalService:
    """
    User-isolated document retrieval service.
    Exposes clean semantic search for future AI agent evidence consumption.
    Strictly forbids financial math - returns evidence only.
    """

    def __init__(self):
        self.embedding_provider = get_embedding_provider()

    async def search_documents(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        query: str,
        top_k: Optional[int] = None,
        similarity_threshold: Optional[float] = None,
        document_id: Optional[uuid.UUID] = None,
    ) -> DocumentSearchResponse:
        """
        Executes semantic search:
        1. Validates query.
        2. Generates query vector embedding.
        3. Enforces user_id filtering.
        4. Computes cosine similarity with similarity_threshold and top_k.
        5. Returns structured evidence with metadata.
        """
        clean_query = query.strip()
        if not clean_query:
            return DocumentSearchResponse(query=query, total_results=0, results=[])

        limit = top_k or settings.RETRIEVAL_TOP_K
        threshold = similarity_threshold if similarity_threshold is not None else settings.SIMILARITY_THRESHOLD

        # Generate query vector
        query_vector = self.embedding_provider.embed_text(clean_query)

        # Scoped repository query
        scored_chunks = await DocumentChunkRepository.search_similar_chunks(
            db=db,
            user_id=user_id,
            query_vector=query_vector,
            top_k=limit,
            similarity_threshold=threshold,
            document_id=document_id,
        )

        results = [
            DocumentChunkResult(
                chunk_id=chunk.id,
                document_id=chunk.document_id,
                chunk_index=chunk.chunk_index,
                content=chunk.content,
                score=round(score, 4),
                metadata=chunk.metadata_,
            )
            for chunk, score in scored_chunks
        ]

        return DocumentSearchResponse(
            query=clean_query,
            total_results=len(results),
            results=results,
        )
