"""Embedding generation for RAG using sentence-transformers."""

from __future__ import annotations

import numpy as np
from sentence_transformers import SentenceTransformer


class EmbeddingService:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2") -> None:
        """Initialize embedding model. Uses lightweight model for fast inference."""
        self.model = SentenceTransformer(model_name)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()

    def embed_text(self, text: str) -> np.ndarray:
        """Embed a single text string."""
        if not text or len(text.strip()) == 0:
            return np.zeros(self.embedding_dim)
        return self.model.encode(text, convert_to_numpy=True)

    def embed_batch(self, texts: list[str]) -> np.ndarray:
        """Embed multiple texts efficiently."""
        if not texts:
            return np.zeros((0, self.embedding_dim))
        cleaned_texts = [t for t in texts if t and len(t.strip()) > 0]
        if not cleaned_texts:
            return np.zeros((0, self.embedding_dim))
        return self.model.encode(cleaned_texts, convert_to_numpy=True)
