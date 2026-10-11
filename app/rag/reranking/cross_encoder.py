"""
Module: app/rag/reranking/cross_encoder.py
Package: pakistan-constitution-ai
Purpose: Local cross-attention re-ranking via FlashRank.
"""

from typing import List, Dict, Any
from flashrank import Ranker, RerankRequest


class FlashRankReranker:
    """
    Reranks vector retrieval candidates using a lightweight cross-encoder model.
    """

    def __init__(self, model_name: str = "ms-marco-TinyBERT-L-2-v2"):
        # Compact, fast CPU reranker (~4MB)
        self.ranker = Ranker(model_name=model_name, cache_dir=".cache/flashrank")

    def rerank(self, query: str, candidates: List[Dict[str, Any]], top_n: int = 3) -> List[Dict[str, Any]]:
        if not candidates:
            return []

        # Prepare passages for FlashRank
        passages = [
            {"id": idx, "text": cand["clause_content"], "metadata": cand}
            for idx, cand in enumerate(candidates)
        ]

        rerank_req = RerankRequest(query=query, passages=passages)
        ranked_results = self.ranker.rerank(rerank_req)

        # Extract top_n reranked items
        reranked_candidates = []
        for res in ranked_results[:top_n]:
            item = res["metadata"]
            item["rerank_score"] = float(res["score"])
            reranked_candidates.append(item)

        return reranked_candidates