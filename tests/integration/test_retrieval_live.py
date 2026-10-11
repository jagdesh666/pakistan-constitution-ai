"""
Module: tests/integration/test_retrieval_live.py
Package: pakistan-constitution-ai
Purpose: Integration tests verifying live Hybrid RRF search against PostgreSQL + pgvector
"""

from app.rag.retrieval.hybrid import HybridRetriever


def test_hybrid_retrieval_surfaces_article_25():
    retriever = HybridRetriever(top_k=10)
    query = "Can citizens be discriminated against on the basis of sex?"
    results = retriever.retrieve(query)

    assert len(results) > 0

    # Ensure Article 25 is in the top candidate pool
    article_numbers = [str(r.get("article_number", "")) for r in results[:5]]
    assert "25" in article_numbers

    # Verify candidate payload contains necessary fields
    top_hit = results[0]
    assert "clause_id" in top_hit
    assert "score" in top_hit or "rrf_score" in top_hit
    assert "article_title" in top_hit


def test_hybrid_retrieval_surfaces_article_25a_education():
    retriever = HybridRetriever(top_k=10)
    query = "free and compulsory education for children age limit"
    results = retriever.retrieve(query)

    assert len(results) > 0
    top_labels = [f"{r.get('article_number')}{r.get('article_suffix', '')}" for r in results[:5]]
    assert "25A" in top_labels