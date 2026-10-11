"""
Module: scripts/prepare_clean_corpus.py
Package: pakistan-constitution-ai
Purpose: Extract substantive 280 constitutional articles cleanly,
         starting from PART I and ending after Article 280.
"""

from pathlib import Path
import re

source_txt = Path("data/source/constitution_of_pakistan.txt")
clean_txt = Path("data/source/constitution_clean.txt")

raw = source_txt.read_text(encoding="utf-8")
print(f"Original full text length: {len(raw)} characters")

# 1. Start from PART I (Introductory)
part1_match = re.search(r"\bPART\s+I\b\s*\n\s*Introductory", raw, re.IGNORECASE)
start_idx = part1_match.start() if part1_match else 0
print(f"Substantive text starts at character index: {start_idx}")

# 2. Find Article 280 (The final constitutional article)
# Article 280 deals with "Continuance of Proclamation of Emergency"
art_280_match = re.search(r"^\s*280\.\s+.*", raw[start_idx:], re.MULTILINE)

if art_280_match:
    # Find where the FIRST SCHEDULE begins AFTER Article 280
    art_280_pos = start_idx + art_280_match.start()
    schedule_after_280 = re.search(r"\b(?:FIRST\s+SCHEDULE|\[?FIRST\s+SCHEDULE\]?)\b", raw[art_280_pos:], re.IGNORECASE)

    if schedule_after_280:
        end_idx = art_280_pos + schedule_after_280.start()
        print(f"Found Article 280! Truncated FIRST SCHEDULE at character index: {end_idx}")
        substantive = raw[start_idx:end_idx]
    else:
        # If no explicit "FIRST SCHEDULE" label, take 4000 characters after Article 280 to capture its full clauses
        end_idx = art_280_pos + 4000
        substantive = raw[start_idx:min(len(raw), end_idx)]
        print(f"Captured through end of Article 280 (index {end_idx})")
else:
    print("Article 280 boundary not found; preserving full body text.")
    substantive = raw[start_idx:]

clean_txt.write_text(substantive, encoding="utf-8")
print(f"Clean substantive corpus written to: {clean_txt}")
print(f"Clean substantive text length: {len(substantive)} characters")