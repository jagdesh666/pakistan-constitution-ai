"""
Module: app/rag/evaluation/retrieval_metrics.py
Package: pakistan-constitution-ai
Purpose: Deterministic retrieval evaluation metrics (Hit Rate, Recall@K, MRR)
"""

from typing import List, Dict, Any


class RetrievalEvaluator:
    """Calculates standard Information Retrieval (IR) metrics."""

    @staticmethod
    def is_match(candidate_label: str, expected_articles: List[str]) -> bool:
        """Checks if a retrieved candidate matches any expected statute label."""
        candidate_clean = candidate_label.lower().replace("ppc", "").replace("section", "").replace("article",
                                                                                                    "").strip()
        for exp in expected_articles:
            exp_clean = exp.lower().replace("ppc", "").replace("section", "").replace("article", "").strip()
            if exp_clean and exp_clean == candidate_clean:
                return True
        return False

    def evaluate_query(
            self,
            retrieved_candidates: List[Dict[str, Any]],
            expected_articles: List[str],
            k: int = 5
    ) -> Dict[str, float]:
        """
        Evaluates a single query's retrieved items up to rank K.
        Returns:
            hit_rate: 1.0 if any expected article is in top-K, else 0.0
            recall: fraction of expected articles found in top-K
            mrr: 1 / rank of first relevant article (0.0 if not found in top-K)
        """
        top_k = retrieved_candidates[:k]

        # Track matches
        matched_expected = set()
        first_match_rank = None

        for rank, cand in enumerate(top_k, start=1):
            label = f"{cand.get('article_number', '')}{cand.get('article_suffix', '')}"
            cand_full = f"{cand.get('article', '')} {cand.get('article_title', '')}"

            for exp in expected_articles:
                if self.is_match(label, [exp]) or self.is_match(cand_full, [exp]):
                    matched_expected.add(exp)
                    if first_match_rank is None:
                        first_match_rank = rank

        # Calculate metrics
        hit_rate = 1.0 if len(matched_expected) > 0 else 0.0
        recall = len(matched_expected) / len(expected_articles) if expected_articles else 1.0
        mrr = (1.0 / first_match_rank) if first_match_rank else 0.0

        return {
            f"hit_rate@{k}": round(hit_rate, 4),
            f"recall@{k}": round(recall, 4),
            f"mrr@{k}": round(mrr, 4)
        }


retrieval_evaluator = RetrievalEvaluator()