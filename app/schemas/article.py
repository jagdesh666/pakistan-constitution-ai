"""
Module: app/schemas/article.py
Package: pakistan-constitution-ai
Purpose: Pydantic schemas for Article Explorer and Feedback
"""

from typing import List, Optional
from pydantic import BaseModel, Field
import uuid


class ClauseDetail(BaseModel):
    clause_number: str
    content: str
    token_count: int


class ArticleDetailResponse(BaseModel):
    id: str
    article_number: int
    article_suffix: str
    title: str
    part_number: str
    part_title: str
    chapter_number: Optional[str] = None
    chapter_title: Optional[str] = None
    full_text: str
    clauses: List[ClauseDetail]


class FeedbackRequest(BaseModel):
    request_id: str = Field(..., description="The request_id from the query response")
    rating: int = Field(..., ge=-1, le=1, description="+1 for helpful, -1 for unhelpful")
    reason_category: Optional[str] = Field(None, description="e.g. 'HALLUCINATION', 'INCORRECT_CITATION'")
    notes: Optional[str] = Field(None, description="Optional user comments")


class FeedbackResponse(BaseModel):
    status: str
    feedback_id: str