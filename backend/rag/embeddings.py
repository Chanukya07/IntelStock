"""Embedding generation for RAG using sentence-transformers.

The model is loaded lazily and failures are tolerated: if the model cannot be
downloaded/initialized (e.g. no network access to the model hub), embedding
calls degrade to "no embedding" so RAG simply returns no context instead of
taking down the whole API.
"""

from __future__ import annotations

import numpy as np

DEFAULT_MODEL = "all-MiniLM-L6-v2"
# Output dimension of all-MiniLM-L6-v2; used to size the FAISS index before the
# model is actually loaded.
DEFAULT_DIM = 384


class EmbeddingService:
    def __init__(self, model_name: str = DEFAULT_MODEL) -> None:
        self.model_name = model_name
        self.embedding_dim = DEFAULT_DIM
        self._model = None
        self._load_failed = False

    @property
    def available(self) -> bool:
        """Whether embeddings can currently be produced."""
        return not self._load_failed

    def _ensure_model(self):
        """Lazily load the model on first use; cache the failure if it errors."""
        if self._model is None and not self._load_failed:
            try:
                from sentence_transformers import SentenceTransformer

                self._model = SentenceTransformer(self.model_name)
                self.embedding_dim = self._model.get_sentence_embedding_dimension()
            except Exception as e:  # noqa: BLE001 - any failure disables RAG gracefully
                self._load_failed = True
                print(f"[embeddings] model unavailable, RAG disabled: {e}")
        return self._model

    def embed_text(self, text: str) -> np.ndarray:
        """Embed a single string; returns a zero vector if unavailable."""
        if not text or not text.strip():
            return np.zeros(self.embedding_dim, dtype=np.float32)
        model = self._ensure_model()
        if model is None:
            return np.zeros(self.embedding_dim, dtype=np.float32)
        return model.encode(text, convert_to_numpy=True)

    def embed_batch(self, texts: list[str]) -> np.ndarray:
        """Embed multiple strings; returns an empty array if unavailable."""
        cleaned = [t for t in texts if t and t.strip()]
        if not cleaned:
            return np.zeros((0, self.embedding_dim), dtype=np.float32)
        model = self._ensure_model()
        if model is None:
            return np.zeros((0, self.embedding_dim), dtype=np.float32)
        return model.encode(cleaned, convert_to_numpy=True)
