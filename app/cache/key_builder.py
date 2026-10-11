"""
Module: app/cache/key_builder.py
Package: pakistan-constitution-ai
Purpose: Deterministic, version-aware cache key generator
"""

import hashlib
import re


class CacheKeyBuilder:
    @staticmethod
    def normalize_query(query: str) -> str:
        """
        Normalizes query so minor differences in punctuation/casing
        share the same cache entry.
        Example: "What is Article 25?" and "what is article 25  " -> "what is article 25"
        """
        clean = query.lower().strip()
        clean = re.sub(r"[^\w\s]", "", clean)
        clean = re.sub(r"\s+", " ", clean)
        return clean

    @classmethod
    def build_query_key(cls, query: str, version_tag: str = "pak-constitution-1973-v1") -> str:
        normalized = cls.normalize_query(query)
        query_hash = hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]
        return f"constitution:{version_tag}:query:{query_hash}"


cache_key_builder = CacheKeyBuilder()