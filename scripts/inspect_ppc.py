"""
Diagnostic: Inspect the downloaded PPC file format and structure.
"""
from pathlib import Path

pdf_path = Path("data/source/pakistan_penal_code.pdf")
txt_path = Path("data/source/pakistan_penal_code.txt")

if pdf_path.exists():
    print(f"FOUND PDF: {pdf_path}")
    import pdfplumber
    with pdfplumber.open(str(pdf_path)) as pdf:
        print(f"Total Pages in PPC PDF: {len(pdf.pages)}")
        # Print text of first 2 pages
        sample = "\n".join([page.extract_text() or "" for page in pdf.pages[:2]])
        print("\n--- SAMPLE TEXT (FIRST 2 PAGES) ---")
        print(sample[:600])
elif txt_path.exists():
    print(f"FOUND TXT: {txt_path}")
    sample = txt_path.read_text(encoding="utf-8", errors="ignore")
    print("\n--- SAMPLE TEXT ---")
    print(sample[:600])
else:
    print("❌ ERROR: Could not find 'pakistan_penal_code.pdf' or 'pakistan_penal_code.txt' in data/source/")