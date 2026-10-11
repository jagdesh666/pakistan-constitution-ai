"""
Module: app/rag/retrieval/hybrid.py
Package: pakistan-constitution-ai
Purpose: Hybrid Retriever combining pgvector dense cosine search with PostgreSQL Full-Text Search via RRF.
"""

from typing import List, Dict, Any
from sqlalchemy import text
from app.db.session import SessionLocal

# Resilient import supporting both function and instance styles
try:
    from app.rag.embeddings.sentence_transformer import get_embedding_provider
except ImportError:
    from app.rag.embeddings.sentence_transformer import embedding_provider
    def get_embedding_provider():
        return embedding_provider


class HybridRetriever:
    """
    Executes dense vector search and sparse keyword search in PostgreSQL,
    then combines candidate ranks using Reciprocal Rank Fusion (RRF).
    """

    def __init__(self, top_k: int = 15, rrf_k: int = 60):
        self.top_k = top_k
        self.rrf_k = rrf_k
        self.embed_provider = get_embedding_provider()

    def retrieve(self, query_text: str) -> List[Dict[str, Any]]:
        # 1. Embed user query into vector
        query_vector = self.embed_provider.embed_text(query_text)
        vector_str = f"[{','.join(map(str, query_vector))}]"

        db = SessionLocal()
        try:
            # 2. Dense Vector Candidates (pgvector cosine distance)
            dense_sql = text("""
                SELECT 
                    c.id AS clause_id,
                    c.clause_number,
                    c.content AS clause_content,
                    a.id AS article_id,
                    a.article_number,
                    a.article_suffix,
                    a.title AS article_title,
                    a.part_number,
                    a.part_title,
                    a.full_text AS article_full_text
                FROM embeddings e
                JOIN clauses c ON e.clause_id = c.id
                JOIN articles a ON c.article_id = a.id
                ORDER BY e.embedding <=> CAST(:q_vec AS vector) ASC
                LIMIT :limit;
            """)
            dense_rows = db.execute(
                dense_sql, {"q_vec": vector_str, "limit": self.top_k}
            ).mappings().all()

            # 3. Sparse Lexical Search (Postgres Full-Text Search via plainto_tsquery)
            sparse_sql = text("""
                SELECT 
                    c.id AS clause_id,
                    c.clause_number,
                    c.content AS clause_content,
                    a.id AS article_id,
                    a.article_number,
                    a.article_suffix,
                    a.title AS article_title,
                    a.part_number,
                    a.part_title,
                    a.full_text AS article_full_text
                FROM clauses c
                JOIN articles a ON c.article_id = a.id
                WHERE COALESCE(c.search_vector, to_tsvector('english', c.content)) @@ plainto_tsquery('english', :q_text)
                LIMIT :limit;
            """)
            sparse_rows = db.execute(
                sparse_sql, {"q_text": query_text, "limit": self.top_k}
            ).mappings().all()

            # 4. Reciprocal Rank Fusion (RRF)
            scores: Dict[str, float] = {}
            candidate_map: Dict[str, Dict[str, Any]] = {}

            # Process Dense Ranks
            for rank, row in enumerate(dense_rows):
                cid = str(row["clause_id"])
                scores[cid] = scores.get(cid, 0.0) + (1.0 / (self.rrf_k + rank + 1))
                if cid not in candidate_map:
                    item = dict(row)
                    item["clause_id"] = cid
                    item["article_id"] = str(row["article_id"])
                    item["content"] = row["clause_content"]  # Compatible with stitcher
                    candidate_map[cid] = item

            # Process Sparse Ranks
            for rank, row in enumerate(sparse_rows):
                cid = str(row["clause_id"])
                scores[cid] = scores.get(cid, 0.0) + (1.0 / (self.rrf_k + rank + 1))
                if cid not in candidate_map:
                    item = dict(row)
                    item["clause_id"] = cid
                    item["article_id"] = str(row["article_id"])
                    item["content"] = row["clause_content"]  # Compatible with stitcher
                    candidate_map[cid] = item

            # 5. Sort fused candidates by combined RRF score
            sorted_candidates = []
            for cid, rrf_score in sorted(scores.items(), key=lambda item: item[1], reverse=True)[:self.top_k]:
                item = candidate_map[cid]
                item["score"] = rrf_score
                item["rrf_score"] = rrf_score
                sorted_candidates.append(item)

            return sorted_candidates

        finally:
            db.close()


# Singleton instance for direct imports
hybrid_retriever = HybridRetriever()