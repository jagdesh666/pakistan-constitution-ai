"""
Module: app/rag/embeddings/sentence_transformer.py
Package: pakistan-constitution-ai
Purpose: Ultra-lightweight CPU embedding provider using FastEmbed (50MB RAM footprint)
"""

from typing import List
from fastembed import TextEmbedding


class LocalEmbeddingProvider:
    """
    Generates identical 384-dimensional dense vectors for all-MiniLM-L6-v2
    using FastEmbed ONNX runtime without heavy PyTorch memory overhead.
    """

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model_name = model_name
        # FastEmbed runs on ONNX CPU with <50MB RAM
        self.model = TextEmbedding(model_name=self.model_name)

    def embed_text(self, text: str) -> List[float]:
        """Embeds a single piece of text into a list of floats."""
        embeddings = list(self.model.embed([text]))
        return embeddings[0].tolist()

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Embeds a list of texts in batch."""
        embeddings = list(self.model.embed(texts))
        return [e.tolist() for e in embeddings]


_instance = None


def get_embedding_provider() -> LocalEmbeddingProvider:
    global _instance
    if _instance is None:
        _instance = LocalEmbeddingProvider()
    return _instance


class _EmbeddingProviderProxy:
    def __getattr__(self, name):
        return getattr(get_embedding_provider(), name)


embedding_provider = _EmbeddingProviderProxy()