from backend.rag.retriever import retrieve_knowledge


questions = [
    "What is the Premium Account daily ATM withdrawal limit?",
    "How many confirmed card fraud cases were there in March 2026?",
    "What number should I call about a suspicious transfer?",
    "What is the emergency fraud hotline?",
]

for question in questions:
    print("\n" + "=" * 70)
    print(f"QUESTION: {question}")

    chunks = retrieve_knowledge(question)

    for chunk in chunks:
        print(
            f"\nSource: {chunk['source']} | "
            f"Page: {chunk['page']} | "
            f"Type: {chunk['content_type']} | "
            f"Rerank: {chunk.get('rerank_score')}"
        )
        print(chunk["text"])