import os
from typing import List, Optional
import uuid
import fitz  # PyMuPDF
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.repositories.document_chunk_repository import DocumentChunkRepository
from app.services.chunking_service import TextChunker
from app.services.embeddings.local import get_embedding_provider


class DocumentProcessingService:
    """
    Orchestrates the document ingestion pipeline for RAG:
    Document file -> Text Extraction -> Cleaning -> Chunking -> Embedding -> Persistent Storage.
    Ensures idempotency by clearing existing chunks for the document before reprocessing.
    """

    def __init__(self):
        self.chunker = TextChunker()
        self.embedding_provider = get_embedding_provider()

    @staticmethod
    def extract_text_from_file(file_path: str, mime_type: Optional[str] = None) -> List[dict]:
        """
        Extracts pages/sections of text from supported document types.
        Returns a list of dicts: [{"page": 1, "text": "..."}]
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        _, ext = os.path.splitext(file_path)
        ext = ext.lower().strip()

        pages_data = []

        if ext == ".pdf":
            try:
                doc = fitz.open(file_path)
                for page_num in range(len(doc)):
                    page = doc[page_num]
                    text = page.get_text("text")
                    if text and text.strip():
                        pages_data.append({"page": page_num + 1, "text": text})
            except Exception as e:
                raise ValueError(f"PDF extraction error: {str(e)}") from e

        elif ext in {".txt", ".csv"}:
            try:
                with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
                    if content.strip():
                        pages_data.append({"page": 1, "text": content})
            except Exception as e:
                raise ValueError(f"Text file extraction error: {str(e)}") from e

        elif ext == ".xlsx":
            try:
                import pandas as pd
                excel_data = pd.read_excel(file_path, sheet_name=None)
                sheet_texts = []
                for sheet_name, df in excel_data.items():
                    csv_representation = df.to_csv(index=False)
                    sheet_texts.append(f"Sheet: {sheet_name}\n{csv_representation}")
                full_text = "\n\n".join(sheet_texts)
                if full_text.strip():
                    pages_data.append({"page": 1, "text": full_text})
            except Exception as e:
                raise ValueError(f"Excel extraction error: {str(e)}") from e

        else:
            raise ValueError(f"Unsupported document type for RAG processing: {ext}")

        return pages_data

    async def process_document(
        self,
        db: AsyncSession,
        document: Document,
        file_path: str,
    ) -> List[DocumentChunk]:
        """
        Extracts, chunks, embeds, and stores chunks for a given document.
        Idempotent: removes existing chunks first.
        """
        # 1. Idempotency: delete prior chunks for this document
        await DocumentChunkRepository.delete_by_document_id(db, document.id)

        # 2. Extract text per page
        pages = self.extract_text_from_file(file_path, document.mime_type)
        if not pages:
            return []

        all_text_chunks = []
        global_chunk_idx = 0

        for page_item in pages:
            page_num = page_item.get("page", 1)
            raw_text = page_item.get("text", "")
            base_meta = {
                "page": page_num,
                "filename": document.filename,
                "mime_type": document.mime_type,
            }
            chunks = self.chunker.chunk_text(raw_text, base_metadata=base_meta)
            for c in chunks:
                c.chunk_index = global_chunk_idx
                global_chunk_idx += 1
                all_text_chunks.append(c)

        if not all_text_chunks:
            return []

        # 3. Batch generate embeddings
        chunk_contents = [c.content for c in all_text_chunks]
        embeddings = self.embedding_provider.embed_texts(chunk_contents)

        # 4. Prepare records for repository bulk creation
        records = []
        for text_chunk, emb in zip(all_text_chunks, embeddings):
            records.append({
                "id": uuid.uuid4(),
                "document_id": document.id,
                "user_id": document.user_id,
                "chunk_index": text_chunk.chunk_index,
                "content": text_chunk.content,
                "embedding": emb,
                "metadata_": text_chunk.metadata,
            })

        # 5. Persist to database
        created_chunks = await DocumentChunkRepository.bulk_create_chunks(db, records)
        return created_chunks
