"""
Module: app/db/models/embedding.py
Package: pakistan-constitution-ai
Purpose: Vector embedding model for semantic similarity search
"""

import uuid
from sqlalchemy import Column, String, ForeignKey, DateTime, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from app.db.base import Base


class Embedding(Base):
    __tablename__ = "embeddings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    clause_id = Column(UUID(as_uuid=True), ForeignKey("clauses.id", ondelete="CASCADE"), nullable=False)
    chunk_representation = Column(String(50), nullable=False, default="RAW_TEXT")
    model_name = Column(String(100), nullable=False)
    embedding = Column(Vector(384), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"))

    # Relationships
    clause = relationship("Clause", back_populates="embeddings")