"""
Module: app/rag/routing/query_router.py
Package: pakistan-constitution-ai
Purpose: Query classification and intent routing (Direct vs Semantic vs Out-of-Scope).
"""

import re
from typing import Tuple, Optional


class QueryRouter:
    """
    Directs incoming queries along the most efficient execution path.
    """

    DIRECT_ARTICLE_PATTERN = re.compile(
        r"^(?:what\s+is\s+|tell\s+me\s+about\s+|show\s+|fetch\s+|read\s+)?article\s+(\d+)([a-z]?)\b",
        re.IGNORECASE
    )

    OUT_OF_SCOPE_KEYWORDS = [
        "recipe", "bake", "weather", "cricket score", "movie",
        "python code", "write a poem", "translate to french"
    ]

    @classmethod
    def route_query(cls, query: str) -> Tuple[str, Optional[Tuple[int, str]]]:
        """
        Returns:
            Tuple of (route_type, payload)
            - ("DIRECT_LOOKUP", (article_number, suffix))
            - ("OUT_OF_SCOPE", None)
            - ("SEMANTIC_RAG", None)
        """
        clean_query = query.strip()

        # 1. Check for Direct Article Reference
        match = cls.DIRECT_ARTICLE_PATTERN.search(clean_query)
        if match:
            art_num = int(match.group(1))
            art_suffix = match.group(2).upper()
            return "DIRECT_LOOKUP", (art_num, art_suffix)

        # 2. Out-of-scope heuristic check
        lower_q = clean_query.lower()
        if any(keyword in lower_q for keyword in cls.OUT_OF_SCOPE_KEYWORDS):
            return "OUT_OF_SCOPE", None

        # 3. Default path: Semantic RAG
        return "SEMANTIC_RAG", None