"""
Module: scripts/extract_ppc_text.py
Package: pakistan-constitution-ai
Purpose: Extract clean text from Pakistan Penal Code (PPC) PDF.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import re
import pdfplumber


def extract_ppc(pdf_path: Path, output_txt: Path):
    print("=" * 65)
    print("EXTRACTING PAKISTAN PENAL CODE (PPC)")
    print(f"Source: {pdf_path}")
    print(f"Target: {output_txt}")
    print("=" * 65)

    if not pdf_path.exists():
        print(f"❌ Error: {pdf_path} not found.")
        return

    extracted_pages = []
    with pdfplumber.open(str(pdf_path)) as pdf:
        total = len(pdf.pages)
        print(f"Total Pages: {total}")
        for i, page in enumerate(pdf.pages):
            text = page.extract_text(layout=True)
            if not text:
                continue

            # Strip running page numbers like "Page 12 of 179" or isolated numbers
            cleaned_lines = []
            for line in text.splitlines():
                l_str = line.strip()
                if re.match(r"^\s*Page\s+\d+\s+of\s+\d+\s*$", l_str, re.I):
                    continue
                cleaned_lines.append(l_str)

            extracted_pages.append("\n".join(cleaned_lines))

            if (i + 1) % 30 == 0 or (i + 1) == total:
                print(f"  Processed page {i + 1}/{total}...")

    raw_text = "\n\n".join(extracted_pages)

    # In PPC, the substantive text starts after the Table of Contents at CHAPTER I
    # Look for CHAPTER I followed by "TITLE AND EXTENT" or Section 1
    # We find the second occurrence of "CHAPTER I" (first is in CONTENTS, second is the body)
    all_ch1 = [m.start() for m in re.finditer(r"\bCHAPTER\s+I\b", raw_text, re.I)]
    if len(all_ch1) >= 2:
        start_idx = all_ch1[1]
        print(f"Skipping preliminary CONTENTS index (trimmed first {start_idx} chars)...")
        substantive = raw_text[start_idx:]
    elif all_ch1:
        start_idx = all_ch1[0]
        substantive = raw_text[start_idx:]
    else:
        substantive = raw_text

    with open(output_txt, "w", encoding="utf-8") as f:
        f.write(substantive)

    print("=" * 65)
    print("EXTRACTION COMPLETE!")
    print(f"Saved to: {output_txt} ({output_txt.stat().st_size / 1024:.2f} KB)")
    print("=" * 65)


if __name__ == "__main__":
    src = PROJECT_ROOT / "data" / "source" / "pakistan_penal_code.pdf"
    dst = PROJECT_ROOT / "data" / "source" / "ppc_clean.txt"
    extract_ppc(src, dst)