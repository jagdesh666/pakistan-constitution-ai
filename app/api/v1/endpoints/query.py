"""
Module: app/api/v1/endpoints/query.py
Package: pakistan-constitution-ai
Purpose: RAG Query Endpoint
"""

from fastapi import APIRouter, HTTPException
from app.schemas.query import QueryRequest, QueryResponse
from app.rag.generation.engine import rag_engine

router = APIRouter()


@router.post("/query", response_model=QueryResponse, summary="Submit a constitutional legal question")
def ask_question(payload: QueryRequest):
    try:
        # Convert Pydantic ChatMessage objects to list of dicts for engine
        formatted_history = [
            {"role": msg.role, "content": msg.content}
            for msg in (payload.history or [])
        ]

        result = rag_engine.answer_query(
            query=payload.query,
            history=formatted_history
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG processing failed: {str(e)}")