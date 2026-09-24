from backend.rag.generator import answer_with_rag_details


question = "What is the default daily transfer limit?"

answer, contexts, sources = answer_with_rag_details(question)

print("ANSWER")
print(answer)

print("\nSOURCES")
for source in sources:
    print(source.model_dump())