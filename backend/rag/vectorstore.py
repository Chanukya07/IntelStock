"""FAISS vector store management for RAG."""

from __future__ import annotations

import logging
import os
import pickle
from pathlib import Path

import numpy as np
import faiss

from backend.rag.embeddings import EmbeddingService

logger = logging.getLogger(__name__)


def _default_store_path() -> str:
    """Resolve where index files live.

    Serverless filesystems are read-only outside /tmp, so the repo-local
    default only applies to persistent hosts. RAG_VECTORSTORE_PATH overrides
    both.
    """
    if os.getenv("RAG_VECTORSTORE_PATH"):
        return os.environ["RAG_VECTORSTORE_PATH"]
    return "/tmp/vectorstore" if os.getenv("VERCEL") else "vectorstore"


class VectorStore:
    def __init__(self, vectorstore_path: str | None = None, model_name: str = "all-MiniLM-L6-v2") -> None:
        """Initialize FAISS vector store."""
        self.vectorstore_path = Path(vectorstore_path or _default_store_path())
        try:
            self.vectorstore_path.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            # Read-only deployment bundle: fall back to /tmp so the store still
            # works for this process, just without surviving a cold start.
            logger.warning("Vector store path %s not writable (%s); using /tmp", self.vectorstore_path, exc)
            self.vectorstore_path = Path("/tmp/vectorstore")
            self.vectorstore_path.mkdir(parents=True, exist_ok=True)
        self.embedding_service = EmbeddingService(model_name)
        self.index: faiss.IndexFlatL2 | None = None
        self.metadata: dict[int, str] = {}
        self.metadata_file = self.vectorstore_path / "metadata.pkl"
        self.index_file = self.vectorstore_path / "index.faiss"
        self._load_or_create_index()

    def _load_or_create_index(self) -> None:
        """Load existing index or create new one."""
        if self.index_file.exists() and self.metadata_file.exists():
            self.index = faiss.read_index(str(self.index_file))
            with open(self.metadata_file, "rb") as f:
                self.metadata = pickle.load(f)
        else:
            embedding_dim = self.embedding_service.embedding_dim
            self.index = faiss.IndexFlatL2(embedding_dim)
            self.metadata = {}

    def add_texts(self, texts: list[str], symbol: str = "") -> None:
        """Add texts to vector store."""
        if not texts:
            return

        embeddings = self.embedding_service.embed_batch(texts)
        if len(embeddings) == 0:
            return

        start_idx = self.index.ntotal
        self.index.add(embeddings.astype(np.float32))

        for i, text in enumerate(texts):
            self.metadata[start_idx + i] = {"text": text, "symbol": symbol}

        self._save_index()

    def search(self, query: str, k: int = 5) -> list[dict[str, str]]:
        """Search for similar texts."""
        if self.index.ntotal == 0:
            return []

        query_embedding = self.embedding_service.embed_text(query)
        if np.all(query_embedding == 0):
            return []

        distances, indices = self.index.search(query_embedding.reshape(1, -1).astype(np.float32), k)

        results = []
        for idx in indices[0]:
            if idx in self.metadata:
                results.append(self.metadata[idx])

        return results

    def _save_index(self) -> None:
        """Save index and metadata to disk (best-effort).

        A failed save must not take down indexing: the in-memory index keeps
        serving this process, it just will not survive a restart.
        """
        try:
            faiss.write_index(self.index, str(self.index_file))
            with open(self.metadata_file, "wb") as f:
                pickle.dump(self.metadata, f)
        except OSError as exc:
            logger.warning("Could not persist vector index to %s: %s", self.vectorstore_path, exc)

    def clear(self) -> None:
        """Clear all data."""
        embedding_dim = self.embedding_service.embedding_dim
        self.index = faiss.IndexFlatL2(embedding_dim)
        self.metadata = {}
        self._save_index()
