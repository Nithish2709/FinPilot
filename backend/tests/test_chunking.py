import pytest
from app.services.chunking_service import TextChunker


def test_text_cleaning():
    raw = "   Line 1 with \t extra    spaces. \r\n\r\n\r\n\r\nLine 2 after blanks.   \x00\x08  "
    cleaned = TextChunker.clean_text(raw)
    assert "Line 1 with extra spaces." in cleaned
    assert "Line 2 after blanks." in cleaned
    assert "\x00" not in cleaned
    assert "\r" not in cleaned


def test_chunking_size_and_overlap():
    chunker = TextChunker(chunk_size=50, chunk_overlap=10)
    text = "The quick brown fox jumps over the lazy dog. A bank statement includes transaction details, dates, and amounts."
    chunks = chunker.chunk_text(text, base_metadata={"test": "doc"})

    assert len(chunks) > 1
    # Check deterministic ordering
    for i, c in enumerate(chunks):
        assert c.chunk_index == i
        assert len(c.content) <= 50
        assert c.metadata["test"] == "doc"
        assert "start_char" in c.metadata


def test_empty_or_whitespace_text_handling():
    chunker = TextChunker(chunk_size=100, chunk_overlap=20)
    assert chunker.chunk_text("") == []
    assert chunker.chunk_text("   \n\n\t  ") == []


def test_invalid_chunk_overlap_raises():
    with pytest.raises(ValueError):
        TextChunker(chunk_size=50, chunk_overlap=50)
    with pytest.raises(ValueError):
        TextChunker(chunk_size=50, chunk_overlap=60)
