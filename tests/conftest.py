"""
Module: tests/conftest.py
Package: pakistan-constitution-ai
Purpose: Pytest global fixtures and environment configuration
"""

import sys
from pathlib import Path

# Ensure project root is on Python path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.cache.redis_client import cache_manager


@pytest.fixture(scope="session")
def client():
    """FastAPI test client fixture."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(autouse=True)
def clean_cache():
    """Cleans in-memory cache before each test run for deterministic results."""
    cache_manager.invalidate_all()
    yield