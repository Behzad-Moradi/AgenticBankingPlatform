import asyncio
import json
from pathlib import Path
from statistics import mean

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from ragas.dataset_schema import SingleTurnSample
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.llms import LangchainLLMWrapper
from ragas.metrics import (
    AnswerCorrectness,
    Faithfulness,
    ResponseRelevancy,
    SemanticSimilarity,
)

from backend.rag.generator import answer_with_rag_details


DATASET_PATH = Path("data/evaluation/rag_retrieval.json")


evaluator_llm = LangchainLLMWrapper(
    ChatOpenAI(model="gpt-4.1-mini")
)

evaluator_embeddings = LangchainEmbeddingsWrapper(
    OpenAIEmbeddings(model="text-embedding-3-small")
)


faithfulness = Faithfulness(
    llm=evaluator_llm,
)

response_relevancy = ResponseRelevancy(
    llm=evaluator_llm,
    embeddings=evaluator_embeddings,
)

semantic_similarity = SemanticSimilarity(
    embeddings=evaluator_embeddings,
)

answer_correctness = AnswerCorrectness(
    llm=evaluator_llm,
    embeddings=evaluator_embeddings,
    answer_similarity=semantic_similarity,
)


async def main() -> None:
    with DATASET_PATH.open() as file:
        dataset = json.load(file)

    faithfulness_scores = []
    relevancy_scores = []
    correctness_scores = []

    for example in dataset:
        reference = example["reference_answer"]

        # Unsupported questions are evaluated separately.
        if reference is None:
            continue

        question = example["question"]

        answer, contexts, _ = answer_with_rag_details(question)

        sample = SingleTurnSample(
            user_input=question,
            response=answer,
            retrieved_contexts=contexts,
            reference=reference,
        )

        faithfulness_score = await faithfulness.single_turn_ascore(
            sample
        )

        relevancy_score = await response_relevancy.single_turn_ascore(
            sample
        )

        correctness_score = await answer_correctness.single_turn_ascore(
            sample
        )

        faithfulness_scores.append(faithfulness_score)
        relevancy_scores.append(relevancy_score)
        correctness_scores.append(correctness_score)

        print("\n" + "=" * 70)
        print(f"Question: {question}")
        print(f"Answer: {answer}")
        print(f"Reference: {reference}")
        print(f"Contexts retrieved: {len(contexts)}")
        print(f"Faithfulness: {faithfulness_score:.3f}")
        print(f"Response relevancy: {relevancy_score:.3f}")
        print(f"Answer correctness: {correctness_score:.3f}")

    print("\n" + "=" * 70)
    print("RAG EVALUATION SUMMARY")
    print("=" * 70)

    print(f"Questions evaluated: {len(faithfulness_scores)}")
    print(
        f"Average faithfulness: "
        f"{mean(faithfulness_scores):.3f}"
    )
    print(
        f"Average response relevancy: "
        f"{mean(relevancy_scores):.3f}"
    )
    print(
        f"Average answer correctness: "
        f"{mean(correctness_scores):.3f}"
    )


if __name__ == "__main__":
    asyncio.run(main())