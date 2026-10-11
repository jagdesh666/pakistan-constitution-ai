from pathlib import Path
import re

txt = Path("data/source/constitution_clean.txt").read_text(encoding="utf-8")

matches = list(re.finditer(r".{0,50}\b25\s*A\b.{0,80}", txt, re.IGNORECASE))
print(f"Found {len(matches)} occurrences of '25A'. Showing matches:")
for m in matches[:6]:
    print("---", m.group(0).replace("\n", " ⏎ "))