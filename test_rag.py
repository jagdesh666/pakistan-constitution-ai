"""
End-to-End RAG Pipeline Verification Script
"""

from app.rag.generation.engine import RAGEngine

if __name__ == "__main__":
    print("=" * 65)
    print("INITIALIZING PAKISTAN CONSTITUTION RAG ENGINE...")
    print("=" * 65)
    rag = RAGEngine()

    test_queries = [
        "Can the state discriminate against citizens on the basis of sex?",
        "What does the constitution say about free education for children?",
        "Is torture allowed to extract evidence in Pakistan?"
    ]

    for q in test_queries:
        print(f"\n[QUERY]: {q}")
        response = rag.answer_query(q)
        print(f"[ANSWER]:\n{response['answer']}")
        print(f"\n[CITATIONS]: {response['citations']}")
        print(f"[LATENCY]: Total: {response['latency']['total_ms']}ms | LLM: {response['latency']['llm_ms']}ms")
        print("-" * 65)