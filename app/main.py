"""
Module: app/main.py
Package: pakistan-constitution-ai
Purpose: FastAPI Application Entry Point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.router import api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Production-Grade RAG Platform for the Constitution of Pakistan (1973) & Pakistan Penal Code (PPC).",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Enable CORS for local Streamlit / React frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Router
app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["Root"])
def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "docs": "/docs",
        "health": "/api/v1/health",
    }