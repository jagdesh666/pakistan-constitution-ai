import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.db.session import SessionLocal
from app.db.models import Article

db = SessionLocal()
art2 = db.query(Article).filter(Article.article_number == 2, Article.article_suffix == "").first()
if art2:
    print(f"Article 2 Full Text in DB:\n---\n{art2.full_text}\n---")
    print(f"Clauses ({len(art2.clauses)}):")
    for c in art2.clauses:
        print(f"  Clause {c.clause_number}: {c.content}")
else:
    print("Article 2 not found in DB!")
db.close()