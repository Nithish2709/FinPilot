import re
from typing import Any, Dict, List, Optional
from pydantic import BaseModel

from app.core.config import settings


class TextChunk(BaseModel):
    chunk_index: int
    content: str
    metadata: Dict[str, Any] = {}


class TextChunker:
    """
    Dedicated component for cleaning and chunking document text.
    Maintains deterministic chunk indexing, configurable chunk_size and chunk_overlap,
    and preserves context and metadata.
    """

    def __init__(self, chunk_size: Optional[int] = None, chunk_overlap: Optional[int] = None):
        self.chunk_size = chunk_size or settings.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP

        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("chunk_overlap must be strictly less than chunk_size")

    @staticmethod
    def clean_text(raw_text: str) -> str:
        """
        Normalizes extracted text:
        - Removes excessive whitespace while preserving paragraphs
        - Collapses repeated blank lines
        - Strips extraneous control characters without distorting document fidelity
        """
        if not raw_text:
            return ""

        # Normalize carriage returns and tabs
        text = raw_text.replace("\r\n", "\n").replace("\r", "\n").replace("\t", " ")

        # Remove non-printable control chars except standard whitespace
        text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", text)

        # Collapse excessive blank lines (>2) to double newlines
        text = re.sub(r"\n\s*\n+", "\n\n", text)

        # Collapse horizontal whitespace sequences to single space
        text = re.sub(r"[ ]{2,}", " ", text)

        return text.strip()

    def chunk_text(self, text: str, base_metadata: Optional[Dict[str, Any]] = None) -> List[TextChunk]:
        """
        Splits normalized text into deterministic overlapping chunks.
        """
        cleaned = self.clean_text(text)
        if not cleaned:
            return []

        chunks: List[TextChunk] = []
        start = 0
        text_len = len(cleaned)
        step = self.chunk_size - self.chunk_overlap
        chunk_idx = 0

        while start < text_len:
            end = min(start + self.chunk_size, text_len)
            chunk_str = cleaned[start:end].strip()

            if chunk_str:
                meta = dict(base_metadata or {})
                meta["start_char"] = start
                meta["end_char"] = end
                chunks.append(
                    TextChunk(
                        chunk_index=chunk_idx,
                        content=chunk_str,
                        metadata=meta,
                    )
                )
                chunk_idx += 1

            if end >= text_len:
                break
            start += step

        return chunks
