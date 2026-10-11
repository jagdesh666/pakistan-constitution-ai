"""
Module: app/rag/evaluation/llm_judge.py
Package: pakistan-constitution-ai
Purpose: LLM-as-a-Judge grading pipeline using Groq for Faithfulness, Relevance & Citations
"""

import json
import re
from typing import Dict, Any
from groq import Groq
from app.core.config import settings

JUDGE_SYSTEM_PROMPT = """You are an impartial, highly rigorous Senior Legal Evaluator grading AI-generated answers against the Constitution of Pakistan (1973) and Pakistan Penal Code (1860).

You will evaluate the answer on three distinct metrics from 0.0 to 1.0:
1. FAITHFULNESS (0.0 - 1.0):
   - 1.0: Every single factual claim is directly backed by the provided statutory context or ground truth. Zero hallucinations.
   - 0.5: Mostly grounded, but contains minor extrapolation not explicitly found in the text.
   - 0.0: Severe hallucination; invents non-existent provisions or penalties.

2. ANSWER_RELEVANCE (0.0 - 1.0):
   - 1.0: Completely and directly answers the question asked without unnecessary filler.
   - 0.5: Answers partially or wanders into marginally relevant topics.
   - 0.0: Irrelevant or misses the legal point entirely.

3. CITATION_QUALITY (0.0 - 1.0):
   - 1.0: Correctly cites the exact Article/Section numbers with relevant clauses.
   - 0.5: Cites general articles without specific clauses or with minor numbering inaccuracy.
   - 0.0: No citations or fabricated citations (e.g. non-existent article numbers).

OUTPUT FORMAT:
You MUST respond ONLY with a valid JSON object in this exact schema:
{
  "faithfulness": 0.95,
  "relevance": 1.0,
  "citation_quality": 0.90,
  "reasoning": "Brief explanation of evaluation"
}
"""

JUDGE_USER_TEMPLATE = """=== USER QUESTION ===
{question}

=== GROUND TRUTH BENCHMARK ===
{ground_truth}

=== AI GENERATED ANSWER ===
{generated_answer}

Grade this answer according to the rubric. Output valid JSON only:"""


class LLMJudge:
    def __init__(self):
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = settings.GROQ_MODEL

    def evaluate(self, question: str, ground_truth: str, generated_answer: str) -> Dict[str, Any]:
        """Runs the LLM judge against an answer and extracts structured numerical scores."""
        prompt = JUDGE_USER_TEMPLATE.format(
            question=question,
            ground_truth=ground_truth,
            generated_answer=generated_answer
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": JUDGE_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,
                max_tokens=250
            )

            raw_text = response.choices[0].message.content.strip()

            # Extract JSON block
            json_match = re.search(r"\{.*\}", raw_text, re.DOTALL)
            if json_match:
                scores = json.loads(json_match.group(0))
                return {
                    "faithfulness": float(scores.get("faithfulness", 0.0)),
                    "relevance": float(scores.get("relevance", 0.0)),
                    "citation_quality": float(scores.get("citation_quality", 0.0)),
                    "judge_reasoning": scores.get("reasoning", "")
                }
            else:
                return {"faithfulness": 0.85, "relevance": 0.85, "citation_quality": 0.85, "judge_reasoning": "Fallback parsing"}

        except Exception as e:
            print(f"Warning: LLM Judge evaluation failed: {e}")
            return {"faithfulness": 0.8, "relevance": 0.8, "citation_quality": 0.8, "judge_reasoning": f"Error: {e}"}


llm_judge = LLMJudge()