from langchain.tools import tool
from backend.rag.retriever import retrieve_knowledge

def format_source(chunk: dict) -> str:
    source = chunk["source"]
    page = chunk.get("page", 0)

    if page > 0:
        return f"{source}, page {page}"

    return source

@tool
def search_bank_knowledge(query: str) -> str:
    """Search the bank's knowledge base for policies, products, fees, and documentation."""

    chunks = retrieve_knowledge(query)

    if not chunks:
        return "No relevant bank knowledge was found."

    return "\n\n".join(
        (
            f"[Source: {chunk['source']}, "
            f"Page: {chunk.get('page')}, "
            f"Chunk: {chunk['chunk_index']}]\n"
            f"{chunk['text']}"
        )
        for chunk in chunks
    )