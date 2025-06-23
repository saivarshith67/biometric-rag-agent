import json
from evaluation.evaluation_model import EvaluationModel
from deepeval.test_case import LLMTestCase
from deepeval.evaluate import evaluate
from deepeval.metrics import (
    AnswerRelevancyMetric,
    FaithfulnessMetric,
    ContextualRelevancyMetric,
)
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
import time


def load_evaluations(file_path="./evaluation/evaluations.jsonl"):
    evaluations = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            evaluations.append(json.loads(line.strip()))
    return evaluations


def save_results_to_jsonl(results, file_path="results.jsonl"):
    with open(file_path, "w", encoding="utf-8") as f:
        for result in results:
            f.write(json.dumps(result, ensure_ascii=False) + "\n")


def chunkify(lst, size):
    for i in range(0, len(lst), size):
        yield lst[i : i + size]


if __name__ == "__main__":
    # Step 1: Load evaluation data
    data = load_evaluations()

    # Step 2: Create test cases from the data
    all_test_cases = []
    for item in data:
        all_test_cases.append(
            LLMTestCase(
                input=item["question"],
                actual_output=item["answer"],
                retrieval_context=item["context"].split("\n")
                if isinstance(item["context"], str)
                else item["context"],
            )
        )

    # Step 3: Initialize custom model

    model = ChatOllama(
        model="qwen2.5:0.5b",
        temperature=0
    )
    custom_model = EvaluationModel(model=model)

    # Step 4: Define evaluation metrics
    metrics = [
        AnswerRelevancyMetric(model=custom_model, threshold=0.7, include_reason=True),
        ContextualRelevancyMetric(
            model=custom_model, threshold=0.7, include_reason=True
        ),
        FaithfulnessMetric(model=custom_model, threshold=0.7, include_reason=True),
    ]

    # Step 5: Split into batches of 2 and evaluate
    all_results = []
    for batch_num, test_case_batch in enumerate(chunkify(all_test_cases, 2)):
        print(f"\n🚀 Evaluating batch {batch_num + 1}")
        evaluate(test_cases=test_case_batch, metrics=metrics)
        time.sleep(30)

        # Step 6: Extract and store results
        for case in test_case_batch:
            result_entry = {
                "question": case.input,
                "answer": case.actual_output,
                "context": case.retrieval_context,
                "answer_relevancy_score": case.metric_scores["Answer Relevancy"].score,
                "contextual_relevancy_score": case.metric_scores[
                    "Contextual Accuracy"
                ].score,
                "faithfulness_score": case.metric_scores["Faithfulness"].score,
                "answer_relevancy_reason": case.metric_scores[
                    "Answer Relevancy"
                ].reasoning,
                "contextual_relevancy_reason": case.metric_scores[
                    "Contextual Accuracy"
                ].reasoning,
                "faithfulness_reason": case.metric_scores["Faithfulness"].reasoning,
            }
            all_results.append(result_entry)

    save_results_to_jsonl(all_results)
    print("\n✅ Evaluation completed. Results saved to `results.jsonl`.")
