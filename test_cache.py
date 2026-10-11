"""
Benchmark: Cold Query vs Warm Cached Query
"""

import time
from app.rag.generation.engine import rag_engine
from app.cache.redis_client import cache_manager


def test_cache_performance():
    query = "What does Article 25 say about equality of citizens?"

    print("=" * 70)
    print("TESTING CACHE PERFORMANCE (COLD RUN VS WARM RUN)")
    print("=" * 70)

    # 1. COLD RUN (Cache Miss - Hits DB and Groq)
    print("\n1. EXECUTING COLD RUN (Cache Miss)...")
    t0 = time.time()
    cold_result = rag_engine.answer_query(query)
    cold_time = (time.time() - t0) * 1000

    print(f"   • Cold Latency:    {cold_time:.2f} ms")
    print(f"   • Cache Hit:       {cold_result.get('cache_hit', False)}")
    print(f"   • Citations Found: {len(cold_result.get('citations', []))}")

    # 2. WARM RUN (Cache Hit - Instant Memory Return)
    print("\n2. EXECUTING WARM RUN (Cache Hit with identical query)...")
    t1 = time.time()
    warm_result = rag_engine.answer_query(query)
    warm_time = (time.time() - t1) * 1000

    print(f"   • Warm Latency:    {warm_time:.2f} ms")
    print(f"   • Cache Hit:       {warm_result.get('cache_hit', False)}")
    print(f"   • Citations Found: {len(warm_result.get('citations', []))}")

    # 3. SPEEDUP COMPARISON
    speedup = cold_time / warm_time if warm_time > 0 else 999.0
    print("\n" + "=" * 70)
    print("CACHE TELEMETRY & RESULTS:")
    print(f" • Cold Latency (Full RAG):   {cold_time:.2f} ms")
    print(f" • Warm Latency (Cached):     {warm_time:.2f} ms")
    print(f" • Performance Acceleration:  {speedup:.1f}x FASTER!")
    print(f" • Cache Stats:               {cache_manager.get_stats()}")
    print("=" * 70)


if __name__ == "__main__":
    test_cache_performance()