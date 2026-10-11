"""
Module: app/db/models/audit.py
Package: pakistan-constitution-ai
Purpose: Models for observability, latency tracing, and user feedback
"""

import uuid
from sqlalchemy import Column, String, Float, Integer, Boolean, Text, ForeignKey, DateTime, SmallInteger, text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.db.base import Base


class QueryLog(Base):
    __tablename__ = "query_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    request_id = Column(String(64), nullable=False, unique=True)
    user_query = Column(Text, nullable=False)
    generated_answer = Column(Text, nullable=True)
    route_taken = Column(String(50), nullable=False)
    retrieval_strategy = Column(String(50), nullable=True)
    cache_hit = Column(Boolean, nullable=False, default=False)
    total_latency_ms = Column(Float, nullable=False)
    retrieval_latency_ms = Column(Float, nullable=True)
    llm_latency_ms = Column(Float, nullable=True)
    prompt_tokens = Column(Integer, nullable=True)
    completion_tokens = Column(Integer, nullable=True)
    cited_articles = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"))

    feedbacks = relationship("FeedbackLog", back_populates="query_log", cascade="all, delete-orphan")


class FeedbackLog(Base):
    __tablename__ = "feedback_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    query_id = Column(UUID(as_uuid=True), ForeignKey("query_logs.id", ondelete="CASCADE"), nullable=False)
    rating = Column(SmallInteger, nullable=False)  # +1 or -1
    reason_category = Column(String(50), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"))

    query_log = relationship("QueryLog", back_populates="feedbacks")