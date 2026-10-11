"""
Module: app/api/v1/endpoints/feedback.py
Package: pakistan-constitution-ai
Purpose: User feedback collection endpoint
"""

from fastapi import APIRouter, HTTPException
from app.db.session import SessionLocal
from app.db.models import QueryLog, FeedbackLog
from app.schemas.article import FeedbackRequest, FeedbackResponse

router = APIRouter()


@router.post("/feedback", response_model=FeedbackResponse, summary="Submit thumbs up/down on an answer")
def submit_feedback(payload: FeedbackRequest):
    db = SessionLocal()
    try:
        query_log = db.query(QueryLog).filter(QueryLog.request_id == payload.request_id).first()
        if not query_log:
            raise HTTPException(status_code=404, detail="Original query request_id not found.")

        feedback_entry = FeedbackLog(
            query_id=query_log.id,
            rating=payload.rating,
            reason_category=payload.reason_category,
            notes=payload.notes,
        )
        db.add(feedback_entry)
        db.commit()
        db.refresh(feedback_entry)

        return FeedbackResponse(
            status="SUCCESS",
            feedback_id=str(feedback_entry.id)
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()