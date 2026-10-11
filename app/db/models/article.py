"""
Module: app/db/models/article.py
Package: pakistan-constitution-ai
Purpose: Models for Constitutional Articles, Statutory Sections, and Clauses.
"""

import uuid
from sqlalchemy import Column, String, Integer, Text, ForeignKey, DateTime, text
from sqlalchemy.dialects.postgresql import UUID, TSVECTOR
from sqlalchemy.orm import relationship
from app.db.base import Base


class Article(Base):
    __tablename__ = "articles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    version_id = Column(UUID(as_uuid=True), ForeignKey("document_versions.id", ondelete="CASCADE"), nullable=False)
    law_type = Column(String(50), nullable=False, default="CONSTITUTION")  # 'CONSTITUTION' or 'PPC'
    part_number = Column(String(50), nullable=False)                       # e.g., 'Chapter XXII' for PPC
    part_title = Column(String(255), nullable=False)
    chapter_number = Column(String(50), nullable=True)
    chapter_title = Column(String(255), nullable=True)
    article_number = Column(Integer, nullable=False)                       # Section number in PPC
    article_suffix = Column(String(5), default="")
    title = Column(String(500), nullable=False)
    full_text = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"))

    version = relationship("DocumentVersion", back_populates="articles")
    clauses = relationship("Clause", back_populates="article", cascade="all, delete-orphan")


class Clause(Base):
    __tablename__ = "clauses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    article_id = Column(UUID(as_uuid=True), ForeignKey("articles.id", ondelete="CASCADE"), nullable=False)
    clause_number = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    token_count = Column(Integer, nullable=False)
    search_vector = Column(TSVECTOR, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"))

    article = relationship("Article", back_populates="clauses")
    embeddings = relationship("Embedding", back_populates="clause", cascade="all, delete-orphan")