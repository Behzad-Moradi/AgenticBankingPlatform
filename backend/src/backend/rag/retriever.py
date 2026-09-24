from langchain_openai import OpenAIEmbeddings
import weaviate
import weaviate.classes as wvc
from backend.rag.reranker import rerank_chunks
from dotenv import load_dotenv

load_dotenv()

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small"
)


def retrieve_knowledge_hybrid(
    question: str,
    limit: int = 3,
    alpha: float = 0.75,
) -> list[dict]:
    query_vector = embeddings.embed_query(question)

    client = weaviate.connect_to_local()

    try:
        collection = client.collections.use("BankKnowledge")

        response = collection.query.hybrid(
            query=question,
            vector=query_vector,
            alpha=alpha,
            limit=limit,
            return_metadata=wvc.query.MetadataQuery(
                score=True,
                explain_score=True,
            ),
        )

        return [
            {
                "text": obj.properties["text"],
                "source": obj.properties["source"],
                "page": obj.properties["page"],
                "chunk_index": obj.properties["chunk_index"],
                "content_type": obj.properties["content_type"],
                "score": obj.metadata.score,
            }
            for obj in response.objects
        ]

    finally:
        client.close()


def retrieve_knowledge(
    question: str,
    limit: int = 3,
) -> list[dict]:

    candidates = retrieve_knowledge_hybrid(
        question=question,
        limit=limit,
        alpha=0.75,
    )

    return rerank_chunks(
        question=question,
        chunks=candidates,
        min_score=0.7,
    )