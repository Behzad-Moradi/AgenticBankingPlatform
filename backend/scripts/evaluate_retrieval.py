import json
from pathlib import Path

from backend.rag.retriever import retrieve_knowledge


DATASET_PATH = Path("data/evaluation/rag_retrieval.json")


def main() -> None:
    with DATASET_PATH.open() as file:
        dataset = json.load(file)

    correct = 0
    supported_total = 0
    supported_correct = 0

    unsupported_total = 0
    unsupported_correct = 0

    for example in dataset:
        question = example["question"]
        expected_source = example["expected_source"]

        chunks = retrieve_knowledge(question)

        retrieved_sources = {
            chunk["source"]
            for chunk in chunks
        }

        if expected_source is None:
            unsupported_total += 1
            passed = len(retrieved_sources) == 0
            if passed:
                unsupported_correct += 1
        else:
            supported_total += 1
            passed = expected_source in retrieved_sources
            if passed:
                supported_correct += 1
        if passed:
            correct += 1
        
        if not passed:
            print("\n*** FAILURE ***")
            print(f"Question: {question}")
            print(f"Expected source: {expected_source}")

            if not chunks:
                print("Retrieved: NOTHING")
            else:
                for chunk in chunks:
                    print(
                        f"Retrieved: {chunk['source']} | "
                        f"Rerank score: {chunk.get('rerank_score')}"
                    )
                    print(f"Text: {chunk['text']}")

        print("\n" + "=" * 70)
        print(f"Question: {question}")
        print(f"Expected: {expected_source}")
        print(f"Retrieved: {sorted(retrieved_sources)}")
        print(f"Result: {'PASS' if passed else 'FAIL'}")

    total = len(dataset)
    accuracy = correct / total if total else 0.0

    supported_accuracy = (
        supported_correct / supported_total
        if supported_total
        else 0.0
    )

    rejection_accuracy = (
        unsupported_correct / unsupported_total
        if unsupported_total
        else 0.0
    )

    print("\n" + "=" * 70)
    print(f"Overall: {correct}/{total} ({accuracy:.2%})")

    print(
        f"Supported retrieval: "
        f"{supported_correct}/{supported_total} "
        f"({supported_accuracy:.2%})"
    )

    print(
        f"Unsupported rejection: "
        f"{unsupported_correct}/{unsupported_total} "
        f"({rejection_accuracy:.2%})"
    )


if __name__ == "__main__":
    main()