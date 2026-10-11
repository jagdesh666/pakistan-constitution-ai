"""
Module: tests/unit/test_cache_unit.py
Package: pakistan-constitution-ai
Purpose: Unit tests for CacheKeyBuilder and ResilientCacheManager
"""

import time
from app.cache.key_builder import cache_key_builder
from app.cache.redis_client import ResilientCacheManager


def test_query_normalization():
    # Minor formatting differences should generate the identical cache key
    q1 = "What is Article 25?"
    q2 = "what is article 25"
    q3 = "  WHAT IS ARTICLE 25?   "

    key1 = cache_key_builder.build_query_key(q1)
    key2 = cache_key_builder.build_query_key(q2)
    key3 = cache_key_builder.build_query_key(q3)

    assert key1 == key2 == key3
    assert "constitution:" in key1
    assert "query:" in key1


def test_cache_hit_and_miss_tracking():
    cache = ResilientCacheManager(default_ttl_seconds=60)
    key = "test_key_1"
    payload = {"answer": "Equality of citizens", "citations": ["Article 25"]}

    # Initial Miss
    assert cache.get(key) is None
    assert cache.misses == 1
    assert cache.hits == 0

    # Store in Cache
    cache.set(key, payload)

    # Subsequent Hit
    cached_val = cache.get(key)
    assert cached_val == payload
    assert cache.hits == 1
    assert cache.misses == 1


def test_cache_ttl_expiration():
    # Cache with 1-second TTL
    cache = ResilientCacheManager(default_ttl_seconds=1)
    key = "expiring_key"
    cache.set(key, {"data": "test"}, ttl_seconds=1)

    assert cache.get(key) is not None
    # Wait for TTL expiration
    time.sleep(1.1)
    assert cache.get(key) is None