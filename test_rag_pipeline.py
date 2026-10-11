"""
End-to-End Test: Verifying Grounded Generation, Citations & Latency with Groq
"""

from app.rag.generation.engine import rag_engine


def run_pipeline_test():
    questions = [
        "What does the Constitution say about discrimination on the basis of sex?",
        "Is free education guaranteed for children in Pakistan, and for which age group?",
        "What is high treason under the Constitution and what acts constitute it?",
        "Can a person invent Article 999 under the Constitution?",  # Test hallucination & out-of-scope defense
    ]

    for q in questions:
        print("\n" + "=" * 75)
        print(f"USER QUESTION: {q}")
        print("=" * 75)

        result = rag_engine.answer_query(q)

        print("\n--- AI GROUNDED ANSWER ---")
        print(result["answer"])

        print("\n--- CITATIONS & METRICS ---")
        citations = result.get("citations", [])
        if citations:
            for idx, c in enumerate(citations[:3], start=1):
                print(f" [{idx}] {c.get('article')}: {c.get('title')}")
        else:
            print(" No statutory citations applicable.")

        metrics = result.get("metrics", {})
        print(f"• Retrieval Latency:   {metrics.get('retrieval_latency_ms', 0)} ms")
        print(f"• Groq LLM Latency:    {metrics.get('llm_latency_ms', 0)} ms")
        print(f"• Total Round-Trip:    {metrics.get('total_latency_ms', 0)} ms")
        print(f"• Tokens (Prompt/Out):  {metrics.get('prompt_tokens', 0)} / {metrics.get('completion_tokens', 0)}")
        print(f"• Model:               {metrics.get('model', 'N/A')}")


if __name__ == "__main__":
    run_pipeline_test()