from pydantic import BaseModel, Field
from langchain.chat_models import init_chat_model
from langchain.messages import HumanMessage, SystemMessage
from dotenv import load_dotenv
load_dotenv()

class RerankedChunk(BaseModel):
    chunk_index: int = Field(
        description="Index of the candidate chunk."
    )
    relevance_score: float = Field(
        ge=0.0,
        le=1.0,
        description=(
            "Relevance of this chunk to the question. "
            "0 means irrelevant and 1 means directly answers the question."
        ),
    )


class RerankingResult(BaseModel):
    chunks: list[RerankedChunk]
    


reranker_llm = init_chat_model("gpt-4.1-mini")

structured_reranker = reranker_llm.with_structured_output(RerankingResult)

def rerank_chunks(
    question: str,
    chunks: list[dict],
    min_score: float = 0.7,
) -> list[dict]:
    if not chunks:
        return []

    candidates = "\n\n".join(
        (
            f"Candidate {index}:\n"
            f"{chunk['text']}"
        )
        for index, chunk in enumerate(chunks)
    )

    result = structured_reranker.invoke(
        [
            SystemMessage(
                content=(
                    "You are a retrieval relevance evaluator. "
                    "Score each candidate according to how well it "
                    "answers the user's question. "
                    "Use a score from 0 to 1. "
                    "A high score means the candidate directly contains "
                    "information needed to answer the question. "
                    "Do not give a high score merely because the candidate "
                    "is generally related to banking."
                )
            ),
            HumanMessage(
                content=(
                    f"Question:\n{question}\n\n"
                    f"Candidates:\n{candidates}"
                )
            ),
        ]
    )

    scored_chunks = []

    for item in result.chunks:
        if (
            item.chunk_index < 0
            or item.chunk_index >= len(chunks)
            or item.relevance_score < min_score
        ):
            continue

        chunk = chunks[item.chunk_index].copy()
        chunk["rerank_score"] = item.relevance_score
        scored_chunks.append(chunk)

    return sorted(
        scored_chunks,
        key=lambda chunk: chunk["rerank_score"],
        reverse=True,
    )