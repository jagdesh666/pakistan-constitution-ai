"""
Module: app/rag/ingestion/parser.py
Package: pakistan-constitution-ai
Purpose: High-accuracy legal parser with footnote filtering and strict Part boundary scoping.
"""

import hashlib
import re
from typing import List, Optional, Dict
from pydantic import BaseModel, Field


class ParsedClause(BaseModel):
    clause_number: str
    content: str
    token_count: int


class ParsedArticle(BaseModel):
    part_number: str
    part_title: str
    chapter_number: Optional[str] = None
    chapter_title: Optional[str] = None
    article_number: int
    article_suffix: str = ""
    title: str
    full_text: str
    clauses: List[ParsedClause] = Field(default_factory=list)


class LegalConstitutionParser:
    PART_PATTERN = re.compile(r"^\s*PART\s+([IVXLCDM]+)\b\s*(.*)$", re.MULTILINE | re.IGNORECASE)
    CHAPTER_PATTERN = re.compile(r"^\s*CHAPTER\s+(\d+|[IVXLCDM]+)[\.\s\-]*(.*)$", re.MULTILINE | re.IGNORECASE)

    # Footnote patterns commonly found in Pakistani statutory PDFs
    FOOTNOTE_INDICATORS = [
        "subs. by", "ins. by", "omitted by", "amdt.", "act no.",
        "constitution of pakistan", "w.e.f.", "added by"
    ]

    ARTICLE_HEADER_PATTERN = re.compile(
        r"^(?:[A-Za-z\s,\-]{0,35})?\[?\b(\d{1,3})\s*([A-Z]?)\s*\]?[\.\-]\s*(.*)$",
        re.MULTILINE
    )

    CLAUSE_PATTERN = re.compile(r"\((\d+[a-z]?)\)\s*(.*?)(?=(?:\(\d+[a-z]?\)|\Z))", re.DOTALL)

    @staticmethod
    def compute_sha256(text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def is_footnote_line(self, line: str) -> bool:
        lower = line.lower()
        if any(ind in lower for ind in self.FOOTNOTE_INDICATORS):
            return True
        if re.match(r"^[\-\—\_\s]{5,}$", line):
            return True
        return False

    def parse(self, raw_text: str) -> List[ParsedArticle]:
        lines = raw_text.splitlines()
        n = len(lines)
        i = 0

        curr_part_num = "Part I"
        curr_part_title = "Introductory"
        curr_chap_num = None
        curr_chap_title = None

        articles_dict: Dict[str, ParsedArticle] = {}

        while i < n:
            line = lines[i].strip()

            # 1. Skip footnote blocks
            if self.is_footnote_line(line):
                i += 1
                continue

            # 2. Part check
            p_m = self.PART_PATTERN.match(line)
            if p_m:
                curr_part_num = f"Part {p_m.group(1).upper()}"
                cand_title = p_m.group(2).strip(". -")
                if not cand_title and i + 1 < n and lines[i + 1].strip():
                    curr_part_title = lines[i + 1].strip()
                    i += 1
                else:
                    curr_part_title = cand_title or "General"
                i += 1
                continue

            # 3. Chapter check
            c_m = self.CHAPTER_PATTERN.match(line)
            if c_m:
                curr_chap_num = f"Chapter {c_m.group(1)}"
                curr_chap_title = c_m.group(2).strip(". -") or "General"
                i += 1
                continue

            # 4. Article Header check
            a_m = self.ARTICLE_HEADER_PATTERN.match(line)
            if a_m and not self.is_footnote_line(line):
                art_num = int(a_m.group(1))
                art_sfx = a_m.group(2).upper()
                first_line_rest = a_m.group(3).strip()

                if 1 <= art_num <= 280:
                    art_key = f"{art_num}_{art_sfx}"

                    # Collect body lines until next Article or Part
                    body_lines = [first_line_rest] if first_line_rest else []
                    i += 1
                    while i < n:
                        peek = lines[i].strip()
                        # If we encounter a footnote line, ignore it
                        if self.is_footnote_line(peek):
                            i += 1
                            continue

                        peek_art = self.ARTICLE_HEADER_PATTERN.match(peek)
                        if (peek_art and 1 <= int(peek_art.group(1)) <= 280 and not self.is_footnote_line(peek)) or self.PART_PATTERN.match(peek):
                            break
                        body_lines.append(lines[i])
                        i += 1

                    raw_body = "\n".join(body_lines).strip()
                    full_text = f"Article {art_num}{art_sfx}.\n{raw_body}".strip()

                    # Extract Clauses
                    clauses: List[ParsedClause] = []
                    matches = list(self.CLAUSE_PATTERN.finditer(raw_body))
                    if not matches:
                        clauses.append(
                            ParsedClause(
                                clause_number="1",
                                content=raw_body if raw_body else f"Article {art_num}{art_sfx}",
                                token_count=int(len(raw_body.split()) * 1.3)
                            )
                        )
                    else:
                        for cm in matches:
                            c_no = cm.group(1).strip()
                            c_body = cm.group(2).strip()
                            clauses.append(
                                ParsedClause(
                                    clause_number=c_no,
                                    content=f"({c_no}) {c_body}",
                                    token_count=int(len(c_body.split()) * 1.3)
                                )
                            )

                    # Do not let later Parts overwrite foundational Part I / Part II articles
                    if art_key in articles_dict:
                        existing_part = articles_dict[art_key].part_number
                        # Keep the earlier occurrence if it is Part I or Part II
                        if existing_part in ["Part I", "Part II"] and curr_part_num not in ["Part I", "Part II"]:
                            pass  # Keep authentic Part I/II article
                        elif len(full_text) > len(articles_dict[art_key].full_text):
                            articles_dict[art_key] = ParsedArticle(
                                part_number=curr_part_num,
                                part_title=curr_part_title,
                                chapter_number=curr_chap_num,
                                chapter_title=curr_chap_title,
                                article_number=art_num,
                                article_suffix=art_sfx,
                                title=f"Article {art_num}{art_sfx}",
                                full_text=full_text,
                                clauses=clauses
                            )
                    else:
                        articles_dict[art_key] = ParsedArticle(
                            part_number=curr_part_num,
                            part_title=curr_part_title,
                            chapter_number=curr_chap_num,
                            chapter_title=curr_chap_title,
                            article_number=art_num,
                            article_suffix=art_sfx,
                            title=f"Article {art_num}{art_sfx}",
                            full_text=full_text,
                            clauses=clauses
                        )
                    continue

            i += 1

        return sorted(list(articles_dict.values()), key=lambda a: (a.article_number, a.article_suffix))