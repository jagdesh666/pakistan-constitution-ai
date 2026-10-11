"""
Diagnostic: Locate authentic Article headers in the text.
"""
from pathlib import Path
import re

txt_path = Path("data/source/constitution_of_pakistan.txt")
text = txt_path.read_text(encoding="utf-8")

# Let's search for "The Republic and its territories" (Real Article 1)
# and "Equality of citizens" (Real Article 25)
queries = [
    r"The\s+Republic\s+and\s+its\s+territories",
    r"Equality\s+of\s+citizens",
    r"Right\s+to\s+education",
    r"Security\s+of\s+person",
    r"Inviolability\s+of\s+dignity"
]

print("=" * 60)
print("LOCATING CANONICAL ARTICLE ANCHORS:")
print("=" * 60)

for q in queries:
    m = re.search(q, text, re.IGNORECASE)
    if m:
        start = max(0, m.start() - 100)
        end = min(len(text), m.end() + 150)
        snippet = text[start:end].replace("\n", " ⏎ ")
        print(f"\nFOUND MATCH for '{q}':")
        print(f"Context: ... {snippet} ...")
    else:
        print(f"\n❌ NOT FOUND: '{q}'")