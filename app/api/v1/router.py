"""
Module: app/api/v1/router.py
Package: pakistan-constitution-ai
Purpose: Central router aggregating all v1 REST endpoints
"""

from fastapi import APIRouter
from app.api.v1.endpoints import query, articles, feedback, health, analytics

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(query.router, tags=["RAG Queries"])
api_router.include_router(articles.router, tags=["Articles"])
api_router.include_router(feedback.router, tags=["Feedback"])
api_router.include_router(analytics.router, tags=["Analytics & Observability"])