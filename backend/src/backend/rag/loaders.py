from pathlib import Path
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import base64
import tempfile
from pathlib import Path
import pymupdf
from langchain.chat_models import init_chat_model
from langchain.messages import HumanMessage
from dotenv import load_dotenv
load_dotenv()


vision_llm = init_chat_model("gpt-4.1-mini")

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100,
)

def page_has_images(page: pymupdf.Page) -> bool:
    return len(page.get_images(full=True)) > 0

def load_pdf(path: Path) -> list[dict]:
    reader = PdfReader(path)

    chunks = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""

        if not text.strip():
            continue

        page_chunks = text_splitter.split_text(text)

        for chunk_index, chunk_text in enumerate(page_chunks):
            chunks.append(
                {
                    "text": chunk_text,
                    "source": path.name,
                    "page": page_number,
                    "chunk_index": chunk_index,
                    "content_type": "text",
                }
            )

    return chunks



def render_pdf_pages(
    path: Path,
    output_dir: Path,
) -> list[dict]:
    output_dir.mkdir(parents=True, exist_ok=True)

    document = pymupdf.open(path)

    pages = []

    try:
        for page_index, page in enumerate(document):
            page_number = page_index + 1

            pixmap = page.get_pixmap(
                matrix=pymupdf.Matrix(2, 2),
                alpha=False,
            )

            image_path = (
                output_dir
                / f"{path.stem}_page_{page_number}.png"
            )

            pixmap.save(str(image_path))

            pages.append(
                {
                    "source": path.name,
                    "page": page_number,
                    "image_path": image_path,
                }
            )

    finally:
        document.close()

    return pages

def extract_visual_content(image_path: Path) -> str:
    image_bytes = image_path.read_bytes()

    image_base64 = base64.b64encode(
        image_bytes
    ).decode("utf-8")

    message = HumanMessage(
        content=[
            {
                "type": "text",
                "text": (
                    "Extract the useful banking information from this "
                    "document page for a retrieval system. "
                    "Capture information contained in tables, charts, "
                    "diagrams, infographics, screenshots, and scanned text. "
                    "Preserve exact numbers, fees, limits, phone numbers, "
                    "dates, labels, and relationships. "
                    "For tables, convert rows and columns into clear textual "
                    "statements. For charts, describe the values associated "
                    "with each label. "
                    "Do not add information that is not visible on the page. "
                    "Return only the extracted information."
                ),
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": (
                        "data:image/png;base64,"
                        f"{image_base64}"
                    )
                },
            },
        ]
    )

    response = vision_llm.invoke([message])

    return str(response.content)


def load_multimodal_pdf(path: Path) -> list[dict]:
    reader = PdfReader(path)
    fitz_document = pymupdf.open(path)

    chunks = []

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            for page_index, page in enumerate(reader.pages):
                page_number = page_index + 1

                # -----------------------------
                # 1. Native text
                # -----------------------------

                native_text = page.extract_text() or ""

                if native_text.strip():
                    text_chunks = text_splitter.split_text(
                        native_text
                    )

                    for chunk_index, chunk_text in enumerate(
                        text_chunks
                    ):
                        chunks.append(
                            {
                                "text": chunk_text,
                                "source": path.name,
                                "page": page_number,
                                "chunk_index": chunk_index,
                                "content_type": "text",
                            }
                        )

                # -----------------------------
                # 2. Decide whether vision
                #    processing is necessary
                # -----------------------------

                fitz_page = fitz_document.load_page(page_index)

                if not page_has_images(fitz_page):
                    continue

                print(
                    f"Vision processing: "
                    f"{path.name}, page {page_number}"
                )

                # -----------------------------
                # 3. Render only this page
                # -----------------------------

                pixmap = fitz_page.get_pixmap(
                    matrix=pymupdf.Matrix(2, 2),
                    alpha=False,
                )

                image_path = (
                    temp_path
                    / f"{path.stem}_page_{page_number}.png"
                )

                pixmap.save(str(image_path))

                # -----------------------------
                # 4. Vision extraction
                # -----------------------------

                visual_text = extract_visual_content(
                    image_path
                )

                if not visual_text.strip():
                    continue

                visual_chunks = text_splitter.split_text(
                    visual_text
                )

                for chunk_index, chunk_text in enumerate(
                    visual_chunks
                ):
                    chunks.append(
                        {
                            "text": chunk_text,
                            "source": path.name,
                            "page": page_number,
                            "chunk_index": chunk_index,
                            "content_type": "visual",
                        }
                    )

    finally:
        fitz_document.close()

    return chunks