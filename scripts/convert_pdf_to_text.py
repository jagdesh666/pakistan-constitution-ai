"""
Module: scripts/convert_pdf_to_text.py
Package: pakistan-constitution-ai
Purpose: High-fidelity layout-aware text extraction from Constitution PDF.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import re
import pdfplumber


def clean_legal_text(raw_text: str) -> str:
    """Repairs PDF font kerning errors (e.g. 'C onstitution' -> 'Constitution')."""
    # 1. Fix single character space splits: 'C onstitution' -> 'Constitution'
    text = re.sub(r"\b([A-Z])\s+([a-z]{2,})\b", r"\1\2", raw_text)
    # 2. Fix broken word stems: 'rem ain' -> 'remain', 'term s' -> 'terms'
    text = re.sub(r"(\w{2,})\s+([a-z]{1,2})\b", lambda m: m.group(1) + m.group(2) if len(m.group(2)) <= 2 and not m.group(2) in ["is", "in", "to", "or", "of", "on", "as", "at", "by", "if", "be", "no", "so", "up", "an", "do"] else m.group(0), text)
    # 3. Normalize multiple whitespace
    text = re.sub(r"[ \t]+", " ", text)
    return text


def extract_pdf_accurately(pdf_path: Path, output_txt_path: Path):
    print("=" * 65)
    print("HIGH-FIDELITY PDF EXTRACTION (pdfplumber)")
    print(f"Source: {pdf_path}")
    print(f"Target: {output_txt_path}")
    print("=" * 65)

    if not pdf_path.exists():
        print(f"❌ Error: {pdf_path} not found.")
        return

    extracted_pages = []
    with pdfplumber.open(str(pdf_path)) as pdf:
        total = len(pdf.pages)
        print(f"Total Pages in PDF: {total}")

        for i, page in enumerate(pdf.pages):
            text = page.extract_text(layout=True)
            if not text:
                continue

            cleaned_lines = []
            for line in text.splitlines():
                l_str = line.strip()
                # Skip running page headers / footers
                if re.match(r"^Constitution\s+of\s+Pakistan", l_str, re.I):
                    continue
                if re.match(r"^\s*\[?\s*\d+\s*\]?\s*$", l_str):
                    continue
                cleaned_lines.append(l_str)

            extracted_pages.append("\n".join(cleaned_lines))

            if (i + 1) % 30 == 0 or (i + 1) == total:
                print(f"  Extracted page {i + 1}/{total}...")

    full_text = "\n\n".join(extracted_pages)
    repaired_text = clean_legal_text(full_text)

    # Skip preliminary TOC: Start right at PART I Introductory
    match = re.search(r"PART\s+I\s*\n\s*Introductory", repaired_text, re.IGNORECASE)
    if match:
        print(f"Skipping Table of Contents (trimmed first {match.start()} chars)...")
        substantive = repaired_text[match.start():]
    else:
        substantive = repaired_text

    with open(output_txt_path, "w", encoding="utf-8") as f:
        f.write(substantive)

    print("=" * 65)
    print("PDF EXTRACTION & REPAIR COMPLETED!")
    print(f"Saved to: {output_txt_path}")
    print("=" * 65)


if __name__ == "__main__":
    src = PROJECT_ROOT / "data" / "source" / "constitution_of_pakistan.pdf"
    dst = PROJECT_ROOT / "data" / "source" / "constitution_of_pakistan.txt"
    extract_pdf_accurately(src, dst)