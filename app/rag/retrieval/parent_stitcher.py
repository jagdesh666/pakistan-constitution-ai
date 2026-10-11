"""
Module: app/rag/retrieval/parent_stitcher.py
Package: pakistan-constitution-ai
Purpose: Maps retrieved child clauses to full parent Articles
"""

from typing import List, Dict, Any
from sqlalchemy import text
from app.db.session import SessionLocal


class ParentContextStitcher:
    """Fetches full parent Articles for retrieved child clauses."""

    @staticmethod
    def stitch(retrieved_chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not retrieved_chunks:
            return []

        # Get unique parent article IDs
        article_ids = list({chunk["article_id"] for chunk in retrieved_chunks})

        db = SessionLocal()
        try:
            sql = text("""
                SELECT 
                    id, 
                    part_number, 
                    part_title, 
                    chapter_number, 
                    chapter_title, 
                    article_number, 
                    article_suffix, 
                    title, 
                    full_text
                FROM articles
                WHERE id IN :a_ids;
            """)

            rows = db.execute(sql, {"a_ids": tuple(article_ids)}).fetchall()
            article_map = {str(r.id): r for r in rows}

            results = []
            seen_articles = set()

            for chunk in retrieved_chunks:
                a_id = chunk["article_id"]
                if a_id in seen_articles:
                    continue
                seen_articles.add(a_id)

                parent = article_map.get(a_id)
                if parent:
                    results.append({
                        "article_id": str(parent.id),
                        "article_number": parent.article_number,
                        "article_suffix": parent.article_suffix,
                        "title": parent.title,
                        "part": f"{parent.part_number}: {parent.part_title}",
                        "chapter": f"{parent.chapter_number or ''}: {parent.chapter_title or ''}".strip(),
                        "matched_clause": chunk["content"],
                        "full_article_text": parent.full_text,
                        "rrf_score": chunk.get("rrf_score", 0.0)
                    })

            return results
        finally:
            db.close()


parent_stitcher = ParentContextStitcher()