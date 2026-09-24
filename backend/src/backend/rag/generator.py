from langchain.chat_models import init_chat_model
from langchain.messages import HumanMessage, SystemMessage
from backend.rag.retriever import retrieve_knowledge
from backend.rag.schemas import KnowledgeSource
from dotenv import load_dotenv
load_dotenv()


def format_source(chunk: dict) -> str:
    source = chunk["source"]
    page = chunk.get("page", 0)

    if page > 0:
        return f"{source}, page {page}"

    return source

llm = init_chat_model("gpt-4.1-mini")

def answer_with_rag(question: str) -> str:
    chunks = retrieve_knowledge(question , limit=1)
    
    if not chunks:
        return (
            "I don't have enough information in the bank's "
            "knowledge base to answer that question."
        )

    context = "\n\n".join(
        f"Source: {format_source(chunk)}\n{chunk['text']}"
        for chunk in chunks
    )

    response = llm.invoke(
        [
            SystemMessage(
                content=(
                    "You are a banking knowledge assistant. "
                    "Answer the user's question using only the provided context. "
                    "If the context does not contain enough information, "
                    "say that you do not have enough information. "
                    "Do not invent banking policies, fees, or product details."
                )
            ),
            HumanMessage(
                content=(
                    f"Context:\n{context}\n\n"
                    f"Question:\n{question}"
                )
            ),
        ]
    )

    return str(response.content)


def answer_with_rag_details(
    question: str,
) -> tuple[str, list[str], list[KnowledgeSource]]:
    chunks = retrieve_knowledge(question)
    
    sources = []

    for chunk in chunks:
        page = chunk.get("page", 0)
        source = KnowledgeSource(
            source=chunk["source"],
            page=page if page > 0 else None,
        )
        if source not in sources:
            sources.append(source)

    if not chunks:
        return (
            "I don't have enough information in the bank's "
            "knowledge base to answer that question.",
            [],
        )

    contexts = [
        chunk["text"]
        for chunk in chunks
    ]

    context = "\n\n".join(
        f"Source: {chunk['source']}\n{chunk['text']}"
        for chunk in chunks
    )

    response = llm.invoke(
        [
            SystemMessage(
                content=(
                    "You are a banking knowledge assistant. "
                    "Answer the user's question using only the provided context. "
                    "If the context does not contain enough information, "
                    "say that you do not have enough information. "
                    "Do not invent banking policies, fees, or product details."
                )
            ),
            HumanMessage(
                content=(
                    f"Context:\n{context}\n\n"
                    f"Question:\n{question}"
                )
            ),
        ]
    )

    return str(response.content), contexts, sources