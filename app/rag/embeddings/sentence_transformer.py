"""
Module: app/rag/embeddings/sentence_transformer.py
Package: pakistan-constitution-ai
Purpose: Local CPU-based embedding generation using Sentence-Transformers with safe cache handling and offline resilience.
"""

import os
from pathlib import Path
from typing import List

# 1. Explicitly configure Hugging Face cache to live inside your project folder
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
LOCAL_CACHE_DIR = PROJECT_ROOT / ".cache" / "huggingface"
os.environ["HF_HOME"] = str(LOCAL_CACHE_DIR)
os.environ["SENTENCE_TRANSFORMERS_HOME"] = str(LOCAL_CACHE_DIR)

# 2. Tell Hugging Face to prefer local disk cache and stop waiting on internet update checks
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

from sentence_transformers import SentenceTransformer
from app.core.config import settings


class LocalEmbeddingProvider:
    """
    Generates dense vector embeddings using local sentence-transformers.
    Default: 'all-MiniLM-L6-v2' (384 dimensions).
    """

    def __init__(self, model_name: str = settings.EMBEDDING_MODEL_NAME):
        self.model_name = model_name
        print(f"Loading embedding model: '{self.model_name}' (Offline Cache Mode)...")

        # Attempt to load model directly from local disk first
        try:
            self.model = SentenceTransformer(
                self.model_name,
                cache_folder=str(LOCAL_CACHE_DIR),
                local_files_only=True,
            )
        except Exception:
            # Fallback: if weights are not yet in local cache, allow online download
            print("Local cache miss or first-time load, enabling network check...")
            os.environ["HF_HUB_OFFLINE"] = "0"
            os.environ["TRANSFORMERS_OFFLINE"] = "0"
            self.model = SentenceTransformer(
                self.model_name,
                cache_folder=str(LOCAL_CACHE_DIR),
            )
            # Re-enable offline mode for subsequent queries
            os.environ["HF_HUB_OFFLINE"] = "1"
            os.environ["TRANSFORMERS_OFFLINE"] = "1"

    def embed_text(self, text: str) -> List[float]:
        """Embeds a single piece of text into a list of floats."""
        embedding = self.model.encode(text, normalize_embeddings=True)
        return embedding.tolist()

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Embeds a list of texts in batch for high performance."""
        embeddings = self.model.encode(texts, batch_size=32, normalize_embeddings=True)
        return embeddings.tolist()


# Lazy singleton pattern
_instance = None


def get_embedding_provider() -> LocalEmbeddingProvider:
    global _instance
    if _instance is None:
        _instance = LocalEmbeddingProvider()
    return _instance


# Export direct instance for backward compatibility across modules
class _EmbeddingProviderProxy:
    def __getattr__(self, name):
        return getattr(get_embedding_provider(), name)


embedding_provider = _EmbeddingProviderProxy()