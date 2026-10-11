"""
Module: app/db/models/document.py
Package: pakistan-constitution-ai
Purpose: Document versions model tracking ingested texts and statutory types.
"""

import uuid
from sqlalchemy import Column, String, Boolean, DateTime, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base


class DocumentVersion(Base):
    __tablename__ = "document_versions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    version_tag = Column(String(50), nullable=False, unique=True)
    law_type = Column(String(50), nullable=False, default="CONSTITUTION")  # 'CONSTITUTION' or 'PPC'
    source_filename = Column(String(255), nullable=False)
    source_sha256 = Column(String(64), nullable=False)
    is_active = Column(Boolean, nullable=False, default=False)
    ingestion_status = Column(String(30), nullable=False, default="PENDING")
    created_at = Column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"))
    activated_at = Column(DateTime(timezone=True), nullable=True)

    articles = relationship("Article", back_populates="version", cascade="all, delete-orphan")