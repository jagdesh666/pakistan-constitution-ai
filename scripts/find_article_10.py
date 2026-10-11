from pathlib import Path
import re

txt = Path("data/source/constitution_clean.txt").read_text(encoding="utf-8")

matches = list(re.finditer(r".{0,50}\b10\b.{0,80}", txt))
print(f"Found {len(matches)} occurrences of '10'. Showing first 5 around Fundamental Rights:")
for m in matches[:6]:
    print("---", m.group(0).replace("\n", " ⏎ "))