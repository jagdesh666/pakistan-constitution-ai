"""
Module: scripts/ingest_ppc.py
Package: pakistan-constitution-ai
Purpose: Ingest Pakistan Penal Code (PPC) into PostgreSQL with vector embeddings.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import re
import hashlib
from typing import List, Dict
from pydantic import BaseModel, Field
from app.db.session import SessionLocal
from app.db.models import DocumentVersion, Article, Clause, Embedding
from app.rag.embeddings.sentence_transformer import get_embedding_provider


class ParsedSection(BaseModel):
    chapter_number: str
    chapter_title: str
    section_number: int
    section_suffix: str = ""
    title: str
    full_text: str
    clauses: List[str] = Field(default_factory=list)


def parse_ppc(raw_text: str) -> List[ParsedSection]:
    lines = raw_text.splitlines()
    n = len(lines)
    i = 0

    curr_chapter_num = "Chapter I"
    curr_chapter_title = "Introduction"

    chap_pattern = re.compile(r"^\s*CHAPTER\s+([IVXLCDM]+|\d+)\s*$", re.I)
    sec_pattern = re.compile(r"^\s*\[?\b(\d{1,3})([A-Z]?)\s*\]?[\.\-]\s*(.*)$")

    sections: Dict[str, ParsedSection] = {}

    while i < n:
        line = lines[i].strip()

        # Chapter transition
        c_m = chap_pattern.match(line)
        if c_m:
            curr_chapter_num = f"Chapter {c_m.group(1).upper()}"
            if i + 1 < n and lines[i + 1].strip():
                curr_chapter_title = lines[i + 1].strip()
                i += 1
            i += 1
            continue

        # Section transition
        s_m = sec_pattern.match(line)
        if s_m:
            sec_num = int(s_m.group(1))
            sec_sfx = s_m.group(2).upper()
            first_line = s_m.group(3).strip()

            # PPC Sections run from 1 to 511
            if 1 <= sec_num <= 511:
                sec_key = f"{sec_num}_{sec_sfx}"
                body_lines = [first_line] if first_line else []
                i += 1

                while i < n:
                    peek = lines[i].strip()
                    peek_sec = sec_pattern.match(peek)
                    if (peek_sec and 1 <= int(peek_sec.group(1)) <= 511) or chap_pattern.match(peek):
                        break
                    body_lines.append(lines[i])
                    i += 1

                body_text = "\n".join(body_lines).strip()
                full_text = f"PPC Section {sec_num}{sec_sfx}.\n{body_text}".strip()

                # Chunking: Break into paragraphs or explanations
                paragraphs = [p.strip() for p in body_text.split("\n\n") if p.strip()]
                if not paragraphs:
                    paragraphs = [body_text] if body_text else [f"Section {sec_num}{sec_sfx}"]

                new_sec = ParsedSection(
                    chapter_number=curr_chapter_num,
                    chapter_title=curr_chapter_title,
                    section_number=sec_num,
                    section_suffix=sec_sfx,
                    title=f"Section {sec_num}{sec_sfx}",
                    full_text=full_text,
                    clauses=paragraphs
                )

                if sec_key not in sections or len(full_text) > len(sections[sec_key].full_text):
                    sections[sec_key] = new_sec

                continue

        i += 1

    return sorted(list(sections.values()), key=lambda s: (s.section_number, s.section_suffix))


def run_ppc_ingestion():
    ppc_txt_path = PROJECT_ROOT / "data" / "source" / "ppc_clean.txt"
    if not ppc_txt_path.exists():
        print(f"❌ Error: {ppc_txt_path} not found. Run 'extract_ppc_text.py' first!")
        return

    raw_text = ppc_txt_path.read_text(encoding="utf-8")
    sha256_hash = hashlib.sha256(raw_text.encode("utf-8")).hexdigest()

    print("=" * 65)
    print("PARSING PAKISTAN PENAL CODE (PPC)...")
    sections = parse_ppc(raw_text)
    print(f"Extracted {len(sections)} distinct PPC Sections.")
    print("=" * 65)

    embed_provider = get_embedding_provider()
    db = SessionLocal()
    version_tag = "ppc-act-xlv-1860"

    try:
        # 1. Document Version for PPC
        doc_version = db.query(DocumentVersion).filter(DocumentVersion.version_tag == version_tag).first()
        if not doc_version:
            doc_version = DocumentVersion(
                version_tag=version_tag,
                law_type="PPC",
                source_filename="pakistan_penal_code.pdf",
                source_sha256=sha256_hash,
                is_active=True,
                ingestion_status="PROCESSING"
            )
            db.add(doc_version)
            db.commit()
            db.refresh(doc_version)
        else:
            db.query(Article).filter(Article.version_id == doc_version.id).delete()
            db.commit()

        total_clauses = 0
        total_embeddings = 0

        print("Computing embeddings and committing PPC sections into PostgreSQL...")
        for idx, sec in enumerate(sections, start=1):
            art_orm = Article(
                version_id=doc_version.id,
                law_type="PPC",
                part_number=sec.chapter_number,
                part_title=sec.chapter_title,
                article_number=sec.section_number,
                article_suffix=sec.section_suffix,
                title=sec.title,
                full_text=sec.full_text
            )
            db.add(art_orm)
            db.flush()

            for c_idx, para in enumerate(sec.clauses, start=1):
                cl_orm = Clause(
                    article_id=art_orm.id,
                    clause_number=str(c_idx),
                    content=para,
                    token_count=int(len(para.split()) * 1.3)
                )
                db.add(cl_orm)
                db.flush()
                total_clauses += 1

                # Generate vector
                vector = embed_provider.embed_text(para)
                emb_orm = Embedding(
                    clause_id=cl_orm.id,
                    chunk_representation="RAW_TEXT",
                    model_name=embed_provider.model_name,
                    embedding=vector
                )
                db.add(emb_orm)
                total_embeddings += 1

            if idx % 50 == 0 or idx == len(sections):
                print(f"  Processed {idx}/{len(sections)} sections ({total_clauses} chunks embedded)...")

        doc_version.ingestion_status = "COMPLETED"
        db.commit()

        print("\n" + "=" * 65)
        print("PPC INGESTION SUCCESSFUL!")
        print("=" * 65)
        print(f" • Statute:          Pakistan Penal Code (1860)")
        print(f" • Sections Stored:  {len(sections)}")
        print(f" • Chunks Embedded:  {total_clauses}")
        print("=" * 65)

    except Exception as e:
        db.rollback()
        print(f"❌ Error during PPC ingestion: {e}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    run_ppc_ingestion()