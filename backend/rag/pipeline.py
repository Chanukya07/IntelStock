"""RAG pipeline definition for IntelStock."""

RAG_STEPS = [
    "News Articles",
    "Preprocessing",
    "Chunking",
    "Embeddings",
    "FAISS Storage",
    "Retriever",
    "LLM",
    "Investment Insights",
]
