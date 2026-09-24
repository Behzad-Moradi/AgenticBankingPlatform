from pathlib import Path

from pypdf import PdfReader


PDF_PATH = Path(
    "data/knowledge/pdfs/multimodal_bank_guide.pdf"
)

reader = PdfReader(PDF_PATH)

print(f"Pages: {len(reader.pages)}")

for page_number, page in enumerate(reader.pages, start=1):
    text = page.extract_text() or ""

    print("=" * 70)
    print(f"PAGE {page_number}")
    print("=" * 70)
    print(text)