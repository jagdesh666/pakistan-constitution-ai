"""
Module: app/db/session.py
Package: pakistan-constitution-ai
Purpose: Database engine and session factory
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Engine manages database connections
engine = create_engine(
    settings.database_url,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Automatically tests connection health before using
)

# SessionLocal is the factory used to create new database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Dependency helper to get a database session and safely close it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()