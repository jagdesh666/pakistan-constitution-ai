"""
Diagnostic & Verification Script
"""

from app.core.config import settings, ENV_FILE_PATH
from app.db.session import SessionLocal
from app.db.models import DocumentVersion

print("=" * 60)
print("DIAGNOSTIC REPORT:")
print("=" * 60)
print(f"1. Looking for .env at: {ENV_FILE_PATH}")
print(f"   File exists?         {ENV_FILE_PATH.exists()}")
print(f"2. DB_USER:             '{settings.DB_USER}'")
print(f"3. DB_NAME:             '{settings.DB_NAME}'")
print(f"4. DB_PASSWORD set?     {'YES (Password is loaded)' if settings.DB_PASSWORD else 'NO (PASSWORD IS EMPTY!)'}")
print("=" * 60)

if not settings.DB_PASSWORD:
    print("\n ACTION REQUIRED: Your .env file does not have DB_PASSWORD filled in.")
    print("Open your .env file and make sure it has:")
    print("DB_PASSWORD=your_actual_password\n")
    exit(1)

print("\nConnecting to PostgreSQL via SQLAlchemy...")
try:
    db = SessionLocal()
    versions = db.query(DocumentVersion).all()
    print(" SUCCESS: Connected via SQLAlchemy ORM!")
    print(f" Current document versions found in database: {len(versions)}")
    db.close()
except Exception as e:
    print(f" FAILED ORM Test: {e}")