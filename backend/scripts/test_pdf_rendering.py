from pathlib import Path

from backend.rag.loaders import render_pdf_pages


PDF_PATH = Path(
    "data/knowledge/pdfs/multimodal_bank_guide.pdf"
)

OUTPUT_DIR = Path(
    "data/tmp/rendered_pages"
)

pages = render_pdf_pages(
    PDF_PATH,
    OUTPUT_DIR,
)

for page in pages:
    print(
        f"Source: {page['source']} | "
        f"Page: {page['page']} | "
        f"Image: {page['image_path']}"
    )