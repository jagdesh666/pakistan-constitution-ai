"""
Diagnostic Script: Checks how article headers look in the extracted TXT file.
"""
from pathlib import Path
import re

txt_path = Path("data/source/constitution_of_pakistan.txt")
text = txt_path.read_text(encoding="utf-8")

# Let's search for mentions of Articles 1, 10, 14, 25, 25A, 51, 175, 280
targets = ["1", "10", "14", "25", "25A", "51", "100", "175", "280"]

print("=" * 60)
print("INSPECTING ARTICLE HEADINGS IN EXTRACTED TEXT:")
print("=" * 60)

for t in targets:
    # Match any line containing target number followed by dot or space
    pattern = re.compile(rf"^\s*{t}\s*[\.\-\]].*$", re.MULTILINE)
    matches = list(pattern.finditer(text))
    if matches:
        first = matches[0].group(0).strip()
        print(f"Article {t:5} -> FOUND: '{first[:60]}'")
    else:
        print(f"Article {t:5} -> ❌ NOT MATCHED with standard header pattern")