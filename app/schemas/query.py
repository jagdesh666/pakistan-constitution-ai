"""
Module: app/schemas/query.py
Package: pakistan-constitution-ai
Purpose: Pydantic DTO schemas for query requests and responses
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str = Field(..., description="'user' or 'assistant'")
    content: str = Field(..., description="Message text")


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=1000, description="The legal question to ask")
    history: Optional[List[ChatMessage]] = Field(default=[], description="Prior conversation messages")


class CitationItem(BaseModel):
    article: str
    title: str
    part: Optional[str] = ""
    clause: Optional[str] = ""


class QueryMetrics(BaseModel):
    total_latency_ms: float
    retrieval_latency_ms: float
    llm_latency_ms: float
    prompt_tokens: int
    completion_tokens: int
    model: str


class QueryResponse(BaseModel):
    request_id: str
    query: str
    rewritten_query: Optional[str] = None
    answer: str
    citations: List[CitationItem]
    metrics: QueryMetrics
    latency: Optional[Dict[str, float]] = None  # Compatible with frontend