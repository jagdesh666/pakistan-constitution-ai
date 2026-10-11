"""
Module: app/api/v1/endpoints/articles.py
Package: pakistan-constitution-ai
Purpose: Direct Constitutional Article inspection
"""

from typing import List
from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models import Article, Clause
from app.schemas.article import ArticleDetailResponse, ClauseDetail

router = APIRouter()


@router.get("/articles/{article_number}", response_model=ArticleDetailResponse, summary="Get full Article by number")
def get_article(article_number: int, suffix: str = ""):
    db = SessionLocal()
    try:
        article = (
            db.query(Article)
            .filter(Article.article_number == article_number, Article.article_suffix == suffix)
            .first()
        )
        if not article:
            raise HTTPException(status_code=404, detail=f"Article {article_number}{suffix} not found.")

        clauses = (
            db.query(Clause)
            .filter(Clause.article_id == article.id)
            .order_by(Clause.clause_number.asc())
            .all()
        )

        return ArticleDetailResponse(
            id=str(article.id),
            article_number=article.article_number,
            article_suffix=article.article_suffix,
            title=article.title,
            part_number=article.part_number,
            part_title=article.part_title,
            chapter_number=article.chapter_number,
            chapter_title=article.chapter_title,
            full_text=article.full_text,
            clauses=[
                ClauseDetail(
                    clause_number=c.clause_number,
                    content=c.content,
                    token_count=c.token_count
                )
                for c in clauses
            ]
        )
    finally:
        db.close()