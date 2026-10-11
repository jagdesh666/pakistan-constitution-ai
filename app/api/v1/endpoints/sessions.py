"""
Module: app/api/v1/endpoints/sessions.py
Package: pakistan-constitution-ai
Purpose: Endpoints for loading, saving, and listing persistent conversations.
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Optional, Any
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models.chat import ChatSession, ChatMessageModel

router = APIRouter()


class SaveMessageDTO(BaseModel):
    role: str
    content: str
    rewritten_query: Optional[str] = None
    citations: Optional[List[Any]] = None
    latency: Optional[dict] = None
    request_id: Optional[str] = None


@router.get("/sessions")
def list_sessions(limit: int = 20, db: Session = Depends(get_db)):
    """List recent conversation sessions safely."""
    try:
        sessions = db.query(ChatSession).order_by(ChatSession.updated_at.desc()).limit(limit).all()
        return [{"id": s.id, "title": s.title, "updated_at": str(s.updated_at)} for s in sessions]
    except Exception as e:
        print(f"Error fetching sessions: {e}")
        return []


@router.get("/sessions/{session_id}/messages")
def get_session_messages(session_id: str, db: Session = Depends(get_db)):
    """Load messages for a given session."""
    try:
        session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if not session:
            return []
        return [
            {
                "role": m.role,
                "content": m.content,
                "rewritten_query": m.rewritten_query,
                "citations": m.citations or [],
                "latency": m.latency,
                "request_id": m.request_id,
            }
            for m in session.messages
        ]
    except Exception as e:
        print(f"Error fetching session messages: {e}")
        return []


@router.post("/sessions/{session_id}/messages")
def append_message(session_id: str, msg: SaveMessageDTO, db: Session = Depends(get_db)):
    """Append a message to a session, creating the session if it doesn't exist."""
    try:
        session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
        if not session:
            clean_title = msg.content.strip().replace("\n", " ")
            title = (clean_title[:38] + "...") if len(clean_title) > 38 else clean_title
            session = ChatSession(id=session_id, title=title)
            db.add(session)
            db.flush()

        new_msg = ChatMessageModel(
            session_id=session_id,
            role=msg.role,
            content=msg.content,
            rewritten_query=msg.rewritten_query,
            citations=msg.citations,
            latency=msg.latency,
            request_id=msg.request_id,
        )
        db.add(new_msg)
        db.commit()
        return {"status": "SUCCESS"}
    except Exception as e:
        db.rollback()
        print(f"Error appending message: {e}")
        return {"status": "ERROR", "detail": str(e)}


@router.delete("/sessions/{session_id}")
def delete_session(session_id: str, db: Session = Depends(get_db)):
    """Delete a chat session."""
    try:
        db.query(ChatSession).filter(ChatSession.id == session_id).delete()
        db.commit()
        return {"status": "DELETED"}
    except Exception as e:
        db.rollback()
        return {"status": "ERROR", "detail": str(e)}