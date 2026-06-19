"""Context retriever for RAG queries."""

from __future__ import annotations

from backend.rag.vectorstore import VectorStore
from backend.rag.chunking import chunk_news_articles


class RAGRetriever:
    def __init__(self, vectorstore_path: str = "vectorstore") -> None:
        """Initialize RAG retriever with vector store."""
        self.vectorstore = VectorStore(vectorstore_path)

    def index_news(self, headlines: list[str], symbol: str = "") -> None:
        """Index company news for retrieval."""
        chunks = chunk_news_articles(headlines, chunk_size=300)
        self.vectorstore.add_texts(chunks, symbol=symbol)

    def index_document(self, text: str, symbol: str = "", title: str = "") -> None:
        """Index a document (research report, analysis, etc.)."""
        from backend.rag.chunking import chunk_text
        chunks = chunk_text(text, chunk_size=500, overlap=100)
        enriched_chunks = [f"{title}: {chunk}" if title else chunk for chunk in chunks]
        self.vectorstore.add_texts(enriched_chunks, symbol=symbol)

    def retrieve_context(self, query: str, symbol: str = "", top_k: int = 5) -> str:
        """Retrieve relevant context for a query."""
        results = self.vectorstore.search(query, k=top_k)

        if not results:
            return ""

        context_parts = []
        for result in results:
            text = result.get("text", "")
            if text:
                context_parts.append(text)

        return "\n\n".join(context_parts)

    def retrieve_symbol_context(self, symbol: str, query: str, top_k: int = 5) -> str:
        """Retrieve context specific to a symbol."""
        results = self.vectorstore.search(query, k=top_k)

        if not results:
            return ""

        relevant_results = [
            r for r in results
            if r.get("symbol") == symbol or not r.get("symbol")
        ]

        context_parts = []
        for result in relevant_results[:top_k]:
            text = result.get("text", "")
            if text:
                context_parts.append(text)

        return "\n\n".join(context_parts)

    def clear_index(self) -> None:
        """Clear all indexed documents."""
        self.vectorstore.clear()
