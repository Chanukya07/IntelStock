"""Text chunking strategies for RAG pipeline."""

from __future__ import annotations


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100) -> list[str]:
    """Split text into overlapping chunks for better context retrieval."""
    if not text or len(text) < chunk_size:
        return [text] if text else []

    chunks = []
    start = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunk = text[start:end]

        if chunk.strip():
            chunks.append(chunk)

        start += chunk_size - overlap

    return chunks


def chunk_news_articles(headlines: list[str], chunk_size: int = 300) -> list[str]:
    """Chunk news articles preserving article boundaries."""
    chunks = []

    for headline in headlines:
        if len(headline) > chunk_size:
            chunks.extend(chunk_text(headline, chunk_size=chunk_size, overlap=50))
        else:
            chunks.append(headline)

    return chunks
