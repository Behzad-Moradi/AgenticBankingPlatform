from pathlib import Path
import weaviate
import weaviate.classes as wvc
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from backend.rag.loaders import load_pdf, load_multimodal_pdf
from dotenv import load_dotenv
load_dotenv()

KNOWLEDGE_DIR = Path("data/knowledge")
PDF_DIR = KNOWLEDGE_DIR / "pdfs"
MULTIMODAL_DIR = KNOWLEDGE_DIR / "multimodal"

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small"
)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100,
)


def load_markdown(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8")

    chunks = text_splitter.split_text(text)

    return [
        {
            "text": chunk,
            "source": path.name,
            "page": 0,
            "chunk_index": index,
            "content_type": "text",
        }
        for index, chunk in enumerate(chunks)
    ]


def load_documents() -> list[dict]:
    documents = []

    # Markdown
    for path in KNOWLEDGE_DIR.glob("*.md"):
        documents.extend(load_markdown(path))

    # Normal text PDFs
    for path in PDF_DIR.glob("*.pdf"):
        documents.extend(load_pdf(path))

    # PDFs requiring visual understanding
    for path in MULTIMODAL_DIR.glob("*.pdf"):
        print(f"Processing multimodal PDF: {path.name}")
        documents.extend(load_multimodal_pdf(path))

    return documents


def main():
    documents = load_documents()

    print(f"Loaded {len(documents)} chunks")

    client = weaviate.connect_to_local()

    try:
        # Recreate collection during development
        if client.collections.exists("BankKnowledge"):
            client.collections.delete("BankKnowledge")

        client.collections.create(
            name="BankKnowledge",
            vector_config=wvc.config.Configure.Vectors.self_provided(),
            properties=[
                wvc.config.Property(
                    name="text",
                    data_type=wvc.config.DataType.TEXT,
                ),
                wvc.config.Property(
                    name="source",
                    data_type=wvc.config.DataType.TEXT,
                ),
                wvc.config.Property(
                    name="page",
                    data_type=wvc.config.DataType.INT,
                ),
                wvc.config.Property(
                    name="chunk_index",
                    data_type=wvc.config.DataType.INT,
                ),
                wvc.config.Property(
                    name="content_type",
                    data_type=wvc.config.DataType.TEXT,
                ),
            ],
        )

        collection = client.collections.use("BankKnowledge")

        for document in documents:
            vector = embeddings.embed_query(document["text"])

            collection.data.insert(
                properties={
                    "text": document["text"],
                    "source": document["source"],
                    "page": document["page"],
                    "chunk_index": document["chunk_index"],
                    "content_type": document["content_type"],
                },
                vector=vector,
            )

        print(f"Inserted {len(documents)} chunks into Weaviate.")

    finally:
        client.close()


if __name__ == "__main__":
    main()