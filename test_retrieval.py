"""
Test: Verifying Hybrid Retrieval and Parent-Child Stitching
"""

from app.rag.retrieval.hybrid import hybrid_retriever
from app.rag.retrieval.parent_stitcher import parent_stitcher


def run_test():
    test_queries = [
        "Can women be discriminated against under the law?",
        "What is the punishment for suspending or subverting the Constitution?",
        "Right to free education for children",
    ]

    for q in test_queries:
        print("\n" + "=" * 70)
        print(f"USER QUERY: '{q}'")
        print("=" * 70)

        # 1. Run Hybrid Search (Child Clauses)
        retrieved_clauses = hybrid_retriever.retrieve(q)
        print(f"-> Found {len(retrieved_clauses)} relevant clauses via Hybrid RRF.")

        # 2. Stitch to Parent Articles
        parent_contexts = parent_stitcher.stitch(retrieved_clauses)

        for idx, item in enumerate(parent_contexts, start=1):
            art_no = f"Article {item['article_number']}{item['article_suffix']}"
            print(f"\n[{idx}] {art_no}: {item['title']} (RRF Score: {item['rrf_score']:.4f})")
            print(f"    Matched Clause: {item['matched_clause']}")
            print(f"    Parent Part:    {item['part']}")


if __name__ == "__main__":
    run_test()