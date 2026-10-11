"""
Module: app/rag/generation/engine.py
Package: pakistan-constitution-ai
Purpose: Production Multi-Statute RAG Orchestrator with Deterministic Simplification,
         Conversation Guardrails, In-Memory Caching, and Observability Logging.
"""

import time
import uuid
import re
from typing import Dict, Any, List, Optional
from groq import Groq

from app.core.config import settings
from app.db.session import SessionLocal
from app.db.models import QueryLog
from app.cache.key_builder import cache_key_builder
from app.cache.redis_client import cache_manager
from app.rag.retrieval.hybrid import HybridRetriever
from app.rag.generation.prompts import (
    SYSTEM_PROMPT,
    CONDENSE_PROMPT,
    CONVERSATIONAL_USER_TEMPLATE,
)

# Resilient imports for Reranker & Router (graceful fallback if not yet implemented)
try:
    from app.rag.reranking.cross_encoder import FlashRankReranker
except ImportError:
    class FlashRankReranker:
        def rerank(self, query: str, candidates: List[Dict[str, Any]], top_n: int = 5):
            return candidates[:top_n]

try:
    from app.rag.routing.query_router import QueryRouter
except ImportError:
    class QueryRouter:
        @staticmethod
        def route_query(query: str):
            return "HYBRID_RAG", {}


class RAGEngine:
    # Heuristic patterns for conversational meta-instructions (no new database search needed)
    META_INSTRUCTION_PATTERNS = re.compile(
        r"\b(?:explain\s+(?:in\s+)?(?:easy|simple|easiest|layman|urdu|roman)|"
        r"undertns?|underst[ae]nd\s+me|summarize|short\s+points|bullet\s+points|"
        r"simplify|in\s+simple\s+words?|aasan\s+alfaaz|samjha[do]?|make\s+it\s+simpler?)\b",
        re.IGNORECASE
    )

    def __init__(self):
        self.retriever = HybridRetriever(top_k=20)
        self.reranker = FlashRankReranker()
        self.client = Groq(api_key=settings.GROQ_API_KEY)
        self.max_context_chars = 6000

    def is_meta_instruction(self, text: str) -> bool:
        """Checks if the user prompt is a formatting/simplification request rather than a new search."""
        clean = text.strip().lower()
        if len(clean.split()) <= 8 and self.META_INSTRUCTION_PATTERNS.search(clean):
            return True
        return False

    def _condense_query(self, query: str, history: List[Dict[str, str]]) -> str:
        if not history:
            return query

        formatted_history = []
        for msg in history[-4:]:
            role = "User" if msg["role"] == "user" else "Assistant"
            formatted_history.append(f"{role}: {msg['content'][:300]}")
        history_str = "\n".join(formatted_history)

        try:
            completion = self.client.chat.completions.create(
                model=settings.GROQ_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a legal search intent condenser. If the user is asking to simplify or "
                            "rephrase the previous message, output 'SIMPLIFY_PREVIOUS_CONTEXT'. "
                            "Otherwise, rewrite it into a complete legal query."
                        ),
                    },
                    {
                        "role": "user",
                        "content": CONDENSE_PROMPT.format(chat_history=history_str, question=query),
                    },
                ],
                temperature=0.0,
                max_tokens=60,
            )
            rewritten = completion.choices[0].message.content.strip().strip('"\'')
            return rewritten if rewritten else query
        except Exception:
            return query

    def answer_query(self, query: str, history: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        start_time = time.time()
        request_id = str(uuid.uuid4())
        history = history or []

        # =========================================================
        # 1. CACHE LOOKUP (Sub-10ms Memory Return)
        # =========================================================
        cache_key = cache_key_builder.build_query_key(query)
        if not history:
            cached_result = cache_manager.get(cache_key)
            if cached_result:
                cached_latency = round((time.time() - start_time) * 1000, 2)
                result = dict(cached_result)
                result["request_id"] = request_id
                result["cache_hit"] = True
                if "latency" in result:
                    result["latency"]["total_ms"] = cached_latency
                if "metrics" in result:
                    result["metrics"]["total_latency_ms"] = cached_latency
                return result
        # =========================================================

        effective_query = query
        rewritten_query = None
        is_simplification = False

        # Step 0: Check if this is a meta-simplification request
        if history and (self.is_meta_instruction(query)):
            is_simplification = True
            rewritten_query = "Simplifying previous legal context"
        elif history:
            condensed = self._condense_query(query, history)
            if "SIMPLIFY" in condensed.upper():
                is_simplification = True
                rewritten_query = "Simplifying previous legal context"
            elif condensed and condensed.lower() != query.lower():
                rewritten_query = condensed
                effective_query = condensed

        # Step 1: Query Routing
        if not is_simplification:
            route, payload = QueryRouter.route_query(effective_query)
            if route == "OUT_OF_SCOPE" and not history:
                answer = (
                    "I am specialized strictly in the Constitution of Pakistan (1973) "
                    "and the Pakistan Penal Code (1860). This question appears to be outside the legal domain."
                )
                total_latency = (time.time() - start_time) * 1000
                self._save_query_log(
                    request_id, query, answer, route, False, total_latency, 0.0, 0.0, 0, 0, []
                )
                return {
                    "request_id": request_id,
                    "query": query,
                    "rewritten_query": rewritten_query,
                    "answer": answer,
                    "citations": [],
                    "cited_articles": [],
                    "cache_hit": False,
                    "latency": {
                        "total_ms": round(total_latency, 2),
                        "retrieval_ms": 0.0,
                        "llm_ms": 0.0,
                    },
                    "metrics": {
                        "total_latency_ms": round(total_latency, 2),
                        "retrieval_latency_ms": 0.0,
                        "llm_latency_ms": 0.0,
                        "prompt_tokens": 0,
                        "completion_tokens": 0,
                        "model": settings.GROQ_MODEL,
                    },
                }
        else:
            route = "CONVERSATIONAL_SIMPLIFICATION"

        # Step 2: Retrieval & Context Stitching
        retrieval_ms = 0.0
        citations = []
        stitched_context = ""

        if is_simplification:
            last_assistant_msg = ""
            for m in reversed(history):
                if m["role"] == "assistant":
                    last_assistant_msg = m["content"]
                    break
            stitched_context = f"PREVIOUS LEGAL SYNTHESIS TO SIMPLIFY:\n{last_assistant_msg}"
        else:
            retrieval_start = time.time()
            candidates = self.retriever.retrieve(effective_query)
            retrieval_ms = (time.time() - retrieval_start) * 1000

            # Rerank candidates to top 5 most relevant
            reranked = self.reranker.rerank(effective_query, candidates, top_n=5)

            parent_articles = {}
            for cand in reranked:
                is_ppc = cand.get("law_type") == "PPC" or "Section" in str(cand.get("article_title", ""))
                label = "PPC Section" if is_ppc else "Article"
                art_key = f"{label} {cand['article_number']}{cand.get('article_suffix', '')}"

                if art_key not in parent_articles:
                    art_text = cand.get("article_full_text") or cand.get("content", "")
                    if len(art_text) > 2500:
                        art_text = art_text[:2500] + "\n...[truncated for brevity]..."
                    parent_articles[art_key] = f"[{art_key}: {cand.get('article_title', '')}]\n{art_text}"

                citations.append({
                    "article": art_key,
                    "title": cand.get("article_title", ""),
                    "part": cand.get("part_number", ""),
                    "clause": cand.get("clause_number", "")
                })

            stitched_context = "\n\n---\n\n".join(parent_articles.values())
            if len(stitched_context) > self.max_context_chars:
                stitched_context = stitched_context[:self.max_context_chars] + "\n...[context budget capped]..."

        # Step 3: Format History for Groq
        formatted_history_lines = []
        for msg in history[-4:]:
            role_label = "User" if msg["role"] == "user" else "Assistant"
            formatted_history_lines.append(f"{role_label}: {msg['content'][:300]}")
        history_text = "\n".join(formatted_history_lines) if formatted_history_lines else "None (New Conversation)"

        formatted_prompt = CONVERSATIONAL_USER_TEMPLATE.format(
            chat_history=history_text,
            context=stitched_context,
            question=query,
        )

        # Step 4: Generation via Groq
        llm_start = time.time()
        completion = self.client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": formatted_prompt},
            ],
            temperature=0.2 if is_simplification else 0.0,
            max_tokens=850,
        )
        llm_ms = (time.time() - llm_start) * 1000
        total_latency_ms = (time.time() - start_time) * 1000

        answer = completion.choices[0].message.content.strip()
        usage = completion.usage
        prompt_tokens = usage.prompt_tokens if usage else 0
        completion_tokens = usage.completion_tokens if usage else 0

        # Step 5: Save Audit Log to PostgreSQL
        self._save_query_log(
            request_id=request_id,
            query=query,
            answer=answer,
            route=route,
            cache_hit=False,
            total_latency=total_latency_ms,
            retrieval_latency=retrieval_ms,
            llm_latency=llm_ms,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            citations=citations,
        )

        final_response = {
            "request_id": request_id,
            "query": query,
            "rewritten_query": rewritten_query,
            "answer": answer,
            "citations": citations,
            "cited_articles": [f"{c.get('article', '')}: {c.get('title', '')}" for c in citations],
            "cache_hit": False,
            "latency": {
                "total_ms": round(total_latency_ms, 2),
                "retrieval_ms": round(retrieval_ms, 2),
                "llm_ms": round(llm_ms, 2),
            },
            "metrics": {
                "total_latency_ms": round(total_latency_ms, 2),
                "retrieval_latency_ms": round(retrieval_ms, 2),
                "llm_latency_ms": round(llm_ms, 2),
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "model": settings.GROQ_MODEL,
            },
        }

        # =========================================================
        # 6. WRITE TO CACHE FOR SUBSEQUENT USERS
        # =========================================================
        if not history and route != "OUT_OF_SCOPE":
            cache_manager.set(cache_key, final_response)

        return final_response

    def _save_query_log(
        self,
        request_id: str,
        query: str,
        answer: str,
        route: str,
        cache_hit: bool,
        total_latency: float,
        retrieval_latency: float,
        llm_latency: float,
        prompt_tokens: int,
        completion_tokens: int,
        citations: list,
    ):
        db = SessionLocal()
        try:
            log_entry = QueryLog(
                request_id=request_id,
                user_query=query,
                generated_answer=answer,
                route_taken=route,
                retrieval_strategy="HYBRID_RRF_RERANKED",
                cache_hit=cache_hit,
                total_latency_ms=total_latency,
                retrieval_latency_ms=retrieval_latency,
                llm_latency_ms=llm_latency,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                cited_articles=citations,
            )
            db.add(log_entry)
            db.commit()
        except Exception as e:
            db.rollback()
            print(f"Warning: Failed to save audit log: {e}")
        finally:
            db.close()


# Singleton instance for imports
rag_engine = RAGEngine()