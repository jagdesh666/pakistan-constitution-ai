"""
Module: app/cache/redis_client.py
Package: pakistan-constitution-ai
Purpose: Production cache client with automatic in-memory fallback (No Docker required)
"""

import time
import json
from typing import Optional, Dict, Any


class ResilientCacheManager:
    """
    High-performance cache layer.
    Uses native in-memory dictionary with TTL eviction,
    compatible with local environments without requiring Docker or Redis.
    """

    def __init__(self, default_ttl_seconds: int = 86400):  # 24 hours TTL
        self.default_ttl = default_ttl_seconds
        self._memory_store: Dict[str, Dict[str, Any]] = {}
        self.hits = 0
        self.misses = 0

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Retrieves cached data if key exists and has not expired."""
        entry = self._memory_store.get(key)
        if not entry:
            self.misses += 1
            return None

        # Check expiration (TTL)
        if time.time() > entry["expires_at"]:
            del self._memory_store[key]
            self.misses += 1
            return None

        self.hits += 1
        return json.loads(entry["data"])

    def set(self, key: str, value: Dict[str, Any], ttl_seconds: Optional[int] = None) -> None:
        """Saves data into cache with expiration."""
        ttl = ttl_seconds or self.default_ttl
        self._memory_store[key] = {
            "data": json.dumps(value),
            "expires_at": time.time() + ttl
        }

    def invalidate_all(self) -> None:
        """Clears cache (used when a new constitutional document is ingested)."""
        self._memory_store.clear()

    def get_stats(self) -> Dict[str, Any]:
        """Returns cache telemetry."""
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total > 0 else 0.0
        return {
            "cached_entries": len(self._memory_store),
            "cache_hits": self.hits,
            "cache_misses": self.misses,
            "hit_rate_pct": round(hit_rate, 2)
        }


# Global singleton instance
cache_manager = ResilientCacheManager()