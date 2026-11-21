"""
Module: app/core/config.py
Package: pakistan-constitution-ai
Purpose: Strongly-typed application settings supporting direct Cloud DATABASE_URL
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
ENV_FILE_PATH = PROJECT_ROOT / ".env"
load_dotenv(dotenv_path=ENV_FILE_PATH, override=True)


class Settings(BaseSettings):
    PROJECT_NAME: str = "Pakistan Constitution AI"
    VERSION: str = "1.0.0"

    # Direct Cloud Connection String (Overrides individual DB_* fields if provided)
    DATABASE_URL_ENV: str = os.getenv("DATABASE_URL", "")

    # Individual parameters fallback
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "5432"))
    DB_NAME: str = os.getenv("DB_NAME", "neondb")
    DB_USER: str = os.getenv("DB_USER", "neondb_owner")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")

    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

    EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384

    @property
    def database_url(self) -> str:
        # If full DATABASE_URL is in .env, use it directly
        if self.DATABASE_URL_ENV:
            url = self.DATABASE_URL_ENV.strip().strip("'\"")
            # Ensure psycopg2 driver is specified
            if url.startswith("postgresql://"):
                url = url.replace("postgresql://", "postgresql+psycopg2://", 1)
            # Ensure SSL is enabled for cloud
            if "sslmode=" not in url and ("neon.tech" in url or "supabase" in url):
                sep = "&" if "?" in url else "?"
                url += f"{sep}sslmode=require"
            return url

        # Fallback to individual components
        ssl_suffix = "?sslmode=require" if ("neon.tech" in self.DB_HOST or "supabase" in self.DB_HOST) else ""
        return f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}{ssl_suffix}"


settings = Settings()