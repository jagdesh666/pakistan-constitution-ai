"""
Module: app/rag/retrieval/bm25_retriever.py
Package: pakistan-constitution-ai
Purpose: Sparse keyword retrieval using PostgreSQL Full-Text Search
"""

from typing import List, Dict, Any
from sqlalchemy import text
from app.db.session import SessionLocal


class BM25KeywordRetriever:
    """Retrieves clauses using exact keyword matching and ts_rank."""

    def __init__(self, top_k: int = 10):
        self.top_k = top_k

    def retrieve(self, query: str) -> List[Dict[str, Any]]:
        db = SessionLocal()
        try:
            # PostgreSQL plainto_tsquery automatically handles grammar and tokenization
            sql = text("""
                SELECT 
                    c.id AS clause_id,
                    c.article_id,
                    c.clause_number,
                    c.content,
                    a.article_number,
                    a.article_suffix,
                    a.title AS article_title,
                    ts_rank_cd(c.search_vector, plainto_tsquery('english', :query)) AS score
                FROM clauses c
                JOIN articles a ON c.article_id = a.id
                WHERE c.search_vector @@ plainto_tsquery('english', :query)
                ORDER BY score DESC
                LIMIT :top_k;
            """)

            results = db.execute(sql, {"query": query, "top_k": self.top_k}).fetchall()

            return [
                {
                    "clause_id": str(r.clause_id),
                    "article_id": str(r.article_id),
                    "clause_number": r.clause_number,
                    "content": r.content,
                    "article_number": r.article_number,
                    "article_suffix": r.article_suffix,
                    "article_title": r.article_title,
                    "score": float(r.score),
                    "retriever": "bm25"
                }
                for r in results
            ]
        finally:
            db.close()


bm25_retriever = BM25KeywordRetriever()