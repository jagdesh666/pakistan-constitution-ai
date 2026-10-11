"""
Module: scripts/ingest_constitution.py
Package: pakistan-constitution-ai
Purpose: Ingest cleaned constitutional corpus, parse hierarchy, compute vector embeddings, and commit to PostgreSQL.
"""

import sys
from pathlib import Path

# Add project root to sys.path so 'app' is found from your project folder
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import os
from app.db.session import SessionLocal
from app.db.models import DocumentVersion, Article, Clause, Embedding
from app.rag.ingestion.parser import LegalConstitutionParser
from app.rag.embeddings.sentence_transformer import get_embedding_provider


def run_ingestion(file_path: Path, version_tag: str):
    print("=" * 65)
    print(f"STARTING CONSTITUTIONAL INGESTION: {version_tag}")
    print(f"Reading source file: {file_path}")
    print("=" * 65)

    if not file_path.exists():
        print(f"❌ Error: Target file not found at {file_path}")
        print("Please run 'python scripts/prepare_clean_corpus.py' first!")
        return

    with open(file_path, "r", encoding="utf-8") as f:
        raw_text = f.read()

    parser = LegalConstitutionParser()
    sha256_hash = parser.compute_sha256(raw_text)

    print("Parsing legal hierarchy (Parts, Chapters, Articles, Clauses)...")
    parsed_articles = parser.parse(raw_text)
    print(f"Extracted {len(parsed_articles)} distinct Constitutional Articles.")

    # Initialize the embedding provider
    embed_provider = get_embedding_provider()

    db = SessionLocal()
    try:
        # 1. Manage DocumentVersion
        doc_version = (
            db.query(DocumentVersion)
            .filter(DocumentVersion.version_tag == version_tag)
            .first()
        )

        if not doc_version:
            doc_version = DocumentVersion(
                version_tag=version_tag,
                source_filename=file_path.name,
                source_sha256=sha256_hash,
                is_active=True,
                ingestion_status="PROCESSING",
            )
            db.add(doc_version)
            db.commit()
            db.refresh(doc_version)
            print(f"Created new document version record: {doc_version.id}")
        else:
            print(
                f"Existing version record found ({doc_version.id}). Refreshing articles..."
            )
            # Cascade deletion removes existing child clauses and embeddings cleanly
            db.query(Article).filter(Article.version_id == doc_version.id).delete()
            db.commit()

        # 2. Iterate Articles and Clauses
        total_clauses = 0
        total_embeddings = 0

        print("\nComputing vector embeddings and inserting into PostgreSQL...")
        for idx, p_art in enumerate(parsed_articles, start=1):
            article_orm = Article(
                version_id=doc_version.id,
                part_number=p_art.part_number,
                part_title=p_art.part_title,
                chapter_number=p_art.chapter_number,
                chapter_title=p_art.chapter_title,
                article_number=p_art.article_number,
                article_suffix=p_art.article_suffix,
                title=p_art.title,
                full_text=p_art.full_text,
            )
            db.add(article_orm)
            db.flush()  # Populates article_orm.id for child clauses

            for p_clause in p_art.clauses:
                clause_orm = Clause(
                    article_id=article_orm.id,
                    clause_number=p_clause.clause_number,
                    content=p_clause.content,
                    token_count=p_clause.token_count,
                )
                db.add(clause_orm)
                db.flush()  # Populates clause_orm.id for embedding
                total_clauses += 1

                # Generate dense embedding vector (384 floats)
                vector = embed_provider.embed_text(p_clause.content)

                embedding_orm = Embedding(
                    clause_id=clause_orm.id,
                    chunk_representation="RAW_TEXT",
                    model_name=embed_provider.model_name,
                    embedding=vector,
                )
                db.add(embedding_orm)
                total_embeddings += 1

            if idx % 25 == 0 or idx == len(parsed_articles):
                print(f"  Processed {idx}/{len(parsed_articles)} articles ({total_clauses} clauses embedded)...")

        doc_version.ingestion_status = "COMPLETED"
        db.commit()

        print("\n" + "=" * 65)
        print("INGESTION SUCCESSFUL!")
        print("=" * 65)
        print(f" • Version Tag:       {version_tag}")
        print(f" • Articles Stored:   {len(parsed_articles)}")
        print(f" • Clauses Stored:    {total_clauses}")
        print(f" • Vectors Created:   {total_embeddings} (384-dimensional)")
        print("=" * 65)

    except Exception as e:
        db.rollback()
        print(f"\n❌ Ingestion failed with error: {e}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    # Prioritize the cleaned corpus if available, fallback to raw text
    clean_path = PROJECT_ROOT / "data" / "source" / "constitution_clean.txt"
    raw_path = PROJECT_ROOT / "data" / "source" / "constitution_of_pakistan.txt"

    source_file = clean_path if clean_path.exists() else raw_path
    run_ingestion(source_file, version_tag="1973-constitution-core")