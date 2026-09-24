from pathlib import Path

from backend.rag.loaders import extract_visual_content


IMAGE_PATH = Path(
    "data/tmp/rendered_pages/"
    "multimodal_bank_guide_page_2.png"
)

text = extract_visual_content(IMAGE_PATH)

print(text)