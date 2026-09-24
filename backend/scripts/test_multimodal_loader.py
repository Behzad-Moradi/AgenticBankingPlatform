from pathlib import Path

from backend.rag.loaders import load_multimodal_pdf


PDF_PATH = Path(
    "data/knowledge/multimodal/multimodal_bank_guide.pdf"
)

chunks = load_multimodal_pdf(PDF_PATH)

print(f"Total chunks: {len(chunks)}")

for chunk in chunks:
    print("=" * 70)
    print(
        f"Source: {chunk['source']} | "
        f"Page: {chunk['page']} | "
        f"Type: {chunk['content_type']} | "
        f"Chunk: {chunk['chunk_index']}"
    )
    print()
    print(chunk["text"])