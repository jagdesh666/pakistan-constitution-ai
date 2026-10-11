"""
Module: app/api/v1/endpoints/health.py
Package: pakistan-constitution-ai
Purpose: Deep system health check
"""

from fastapi import APIRouter
from sqlalchemy import text
from app.db.session import SessionLocal

router = APIRouter()


@router.get("/health", summary="Health check probe")
def health_check():
    db_status = "DOWN"
    articles_count = 0

    try:
        db = SessionLocal()
        res = db.execute(text("SELECT count(*) FROM articles;")).scalar()
        articles_count = res
        db_status = "UP"
        db.close()
    except Exception as e:
        db_status = f"ERROR: {str(e)}"

    return {
        "status": "HEALTHY" if db_status == "UP" else "DEGRADED",
        "database": db_status,
        "articles_indexed": articles_count,
        "llm_provider": "Groq",
    }