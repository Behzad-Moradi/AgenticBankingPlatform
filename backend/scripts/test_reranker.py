from backend.rag.reranker import rerank_chunks
from backend.rag.retriever import retrieve_knowledge_hybrid
from dotenv import load_dotenv
load_dotenv()

questions = [
    "How much does it cost to send money overseas?",
    "What should I do if my card is stolen?",
    "Does the savings account have a monthly fee?",
    "Does the bank provide cryptocurrency custody?",
]


for question in questions:
    print("\n" + "=" * 70)
    print(f"Question: {question}")

    candidates = retrieve_knowledge_hybrid(
        question,
        limit=3,
        alpha=0.75,
    )

    print("\nHybrid candidates:")

    for candidate in candidates:
        print(
            f"  {candidate['source']} | "
            f"Hybrid score: {candidate['score']:.3f}"
        )

    reranked = rerank_chunks(
        question,
        candidates,
        min_score=0.7,
    )

    print("\nAfter reranking:")

    if not reranked:
        print("  No sufficiently relevant chunks.")

    for chunk in reranked:
        print(
            f"  {chunk['source']} | "
            f"Rerank score: {chunk['rerank_score']:.3f}"
        )