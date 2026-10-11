"""
Module: app/api/v1/endpoints/analytics.py
Package: pakistan-constitution-ai
Purpose: Observability and Telemetry Analytics API Endpoint
"""

from fastapi import APIRouter
from sqlalchemy import text
from app.db.session import SessionLocal
from app.cache.redis_client import cache_manager

router = APIRouter()


@router.get("/analytics/dashboard", summary="Get aggregated RAG observability metrics")
def get_dashboard_metrics():
    db = SessionLocal()
    try:
        # 1. Total Queries and Latency Averages
        summary_query = text("""
            SELECT 
                COUNT(*) AS total_queries,
                COALESCE(AVG(total_latency_ms), 0) AS avg_latency,
                COALESCE(AVG(retrieval_latency_ms), 0) AS avg_retrieval_ms,
                COALESCE(AVG(llm_latency_ms), 0) AS avg_llm_ms,
                COALESCE(SUM(prompt_tokens), 0) AS total_prompt_tokens,
                COALESCE(SUM(completion_tokens), 0) AS total_completion_tokens
            FROM query_logs;
        """)
        summary_row = db.execute(summary_query).mappings().first()

        # 2. User Feedback Aggregation
        feedback_query = text("""
            SELECT 
                COUNT(*) FILTER (WHERE rating = 1) AS positive_count,
                COUNT(*) FILTER (WHERE rating = -1) AS negative_count
            FROM feedback_logs;
        """)
        feedback_row = db.execute(feedback_query).mappings().first()

        # 3. Recent 10 Queries for Audit Trail
        recent_query = text("""
            SELECT 
                request_id,
                user_query,
                route_taken,
                total_latency_ms,
                created_at
            FROM query_logs
            ORDER BY created_at DESC
            LIMIT 8;
        """)
        recent_rows = db.execute(recent_query).mappings().all()

        recent_logs = [
            {
                "request_id": str(r["request_id"])[:8] + "...",
                "query": r["user_query"],
                "route": r["route_taken"],
                "latency_ms": round(r["total_latency_ms"], 1),
                "timestamp": str(r["created_at"])[:19]
            }
            for r in recent_rows
        ]

        # 4. Cache Telemetry
        cache_stats = cache_manager.get_stats()

        return {
            "overview": {
                "total_queries": summary_row["total_queries"],
                "avg_latency_ms": round(summary_row["avg_latency"], 1),
                "avg_retrieval_ms": round(summary_row["avg_retrieval_ms"], 1),
                "avg_llm_ms": round(summary_row["avg_llm_ms"], 1),
                "total_tokens_consumed": summary_row["total_prompt_tokens"] + summary_row["total_completion_tokens"],
            },
            "cache": cache_stats,
            "feedback": {
                "positive": feedback_row["positive_count"] if feedback_row else 0,
                "negative": feedback_row["negative_count"] if feedback_row else 0,
            },
            "recent_queries": recent_logs
        }

    finally:
        db.close()