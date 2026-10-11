"""
Module: tests/unit/test_parser_unit.py
Package: pakistan-constitution-ai
Purpose: Unit tests for LegalConstitutionParser
"""

from app.rag.ingestion.parser import LegalConstitutionParser

SAMPLE_LEGAL_RAW_TEXT = """
PART II
Fundamental Rights and Principles of Policy

CHAPTER 1. - FUNDAMENTAL RIGHTS

25. Equality of citizens.
(1) All citizens are equal before law and are entitled to equal protection of law.
(2) There shall be no discrimination on the basis of sex.
(3) Nothing in this Article shall prevent the State from making any special provision for the protection of women and children.

25A. Right to education.
The State shall provide free and compulsory education to all children of the age of five to sixteen years in such manner as may be determined by law.
"""


def test_legal_parser_extracts_articles_and_clauses():
    parser = LegalConstitutionParser()
    articles = parser.parse(SAMPLE_LEGAL_RAW_TEXT)

    assert len(articles) == 2

    # Verify Article 25
    art_25 = next((a for a in articles if a.article_number == 25 and a.article_suffix == ""), None)
    assert art_25 is not None
    assert "25" in art_25.title or "Equality" in art_25.title
    assert art_25.part_number == "Part II"
    assert len(art_25.clauses) == 3
    assert "2" in art_25.clauses[1].clause_number
    assert "no discrimination on the basis of sex" in art_25.clauses[1].content

    # Verify Article 25A (Alphanumeric suffix)
    art_25a = next((a for a in articles if a.article_number == 25 and a.article_suffix == "A"), None)
    assert art_25a is not None
    assert "25A" in art_25a.title or "education" in art_25a.title.lower() or "Right" in art_25a.title
    assert "five to sixteen years" in art_25a.clauses[0].content