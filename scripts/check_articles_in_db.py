"""
Diagnostic: Check if specific articles exist in PostgreSQL
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.db.session import SessionLocal
from app.db.models import Article

db = SessionLocal()
targets = [(10, ""), (25, ""), (25, "A"), (14, ""), (2, ""), (3, "")]

print("=" * 60)
print("CHECKING ARTICLES IN POSTGRESQL:")
print("=" * 60)

for num, sfx in targets:
    art = db.query(Article).filter(Article.article_number == num, Article.article_suffix == sfx).first()
    if art:
        clauses_count = len(art.clauses)
        print(f"Article {num}{sfx:2} -> PRESENT in DB! ({clauses_count} clauses) - Title: {art.title[:40]}")
    else:
        print(f"Article {num}{sfx:2} -> ❌ MISSING FROM DB!")

db.close()