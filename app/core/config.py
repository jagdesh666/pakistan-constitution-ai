"""
Module: app/core/config.py
Package: pakistan-constitution-ai
Purpose: Strongly-typed application settings loaded from .env
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# 1. Find the project root and force-load the .env file
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
ENV_FILE_PATH = PROJECT_ROOT / ".env"
load_dotenv(dotenv_path=ENV_FILE_PATH, override=True)


class Settings(BaseSettings):
    # Application Info
    PROJECT_NAME: str = "Pakistan Constitution AI"
    VERSION: str = "1.0.0"

    # PostgreSQL Database Connection
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "5432"))
    DB_NAME: str = os.getenv("DB_NAME", "constitution_db")
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")

    # Groq API Configuration
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

    # Embedding Model
    EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384

    @property
    def database_url(self) -> str:
        """Builds standard synchronous PostgreSQL connection string using psycopg2."""
        return f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


settings = Settings()