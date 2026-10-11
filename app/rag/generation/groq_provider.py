"""
Module: app/rag/generation/groq_provider.py
Package: pakistan-constitution-ai
Purpose: Groq LLM provider for ultra-fast grounded generation
"""

import time
from typing import Dict, Any
from groq import Groq
from app.core.config import settings


class GroqProvider:
    def __init__(self):
        if not settings.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is missing from environment variables.")
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.model = settings.GROQ_MODEL

    def generate(self, system_prompt: str, user_prompt: str, temperature: float = 0.0) -> Dict[str, Any]:
        """
        Executes inference via Groq with deterministic temperature=0.0 to prevent hallucinations.
        """
        start_time = time.perf_counter()

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,  # 0.0 ensures factual, deterministic responses
            max_tokens=1024,
        )

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        choice = response.choices[0].message.content
        usage = response.usage

        return {
            "content": choice,
            "latency_ms": round(latency_ms, 2),
            "prompt_tokens": usage.prompt_tokens if usage else 0,
            "completion_tokens": usage.completion_tokens if usage else 0,
            "model_used": self.model,
        }


groq_provider = GroqProvider()