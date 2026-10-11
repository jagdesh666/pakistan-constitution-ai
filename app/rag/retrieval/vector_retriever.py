"""
Module: app/rag/retrieval/vector_retriever.py
Package: pakistan-constitution-ai
Purpose: Dense semantic vector search using pgvector cosine distance
"""

from typing import List, Dict, Any
from sqlalchemy import text
from app.db.session import SessionLocal
from app.rag.embeddings.sentence_transformer import embedding_provider


class VectorRetriever:
    """Retrieves clauses using pgvector cosine similarity."""

    def __init__(self, top_k: int = 10):
        self.top_k = top_k

    def retrieve(self, query: str) -> List[Dict[str, Any]]:
        # 1. Embed user query into 384 floats
        query_vector = embedding_provider.embed_text(query)
        vector_str = f"[{','.join(map(str, query_vector))}]"

        db = SessionLocal()
        try:
            # 2. Cosine distance query: (1 - distance) = similarity score
            sql = text("""
                SELECT 
                    c.id AS clause_id,
                    c.article_id,
                    c.clause_number,
                    c.content,
                    a.article_number,
                    a.article_suffix,
                    a.title AS article_title,
                    (1 - (e.embedding <=> :query_vector::vector)) AS score
                FROM embeddings e
                JOIN clauses c ON e.clause_id = c.id
                JOIN articles a ON c.article_id = a.id
                ORDER BY e.embedding <=> :query_vector::vector ASC
                LIMIT :top_k;
            """)

            results = db.execute(sql, {"query_vector": vector_str, "top_k": self.top_k}).fetchall()

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
                    "retriever": "vector"
                }
                for r in results
            ]
        finally:
            db.close()


vector_retriever = VectorRetriever()