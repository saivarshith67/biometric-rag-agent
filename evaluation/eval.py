import json
from evaluation.evaluation_model import EvaluationModel
from deepeval.test_case import LLMTestCase
from deepeval.evaluate import evaluate
from deepeval.metrics import AnswerRelevancyMetric, FaithfulnessMetric, ContextualRelevancyMetric
from langchain_openai import ChatOpenAI


def load_evaluations(file_path="./evaluation/evaluations.jsonl"):
    evaluations = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            evaluations.append(json.loads(line.strip()))
    return evaluations


if __name__ == "__main__":
    # Step 1: Load evaluation data
    data = load_evaluations()

    # Step 2: Create test cases from the data
    test_cases = []
    for item in data:
        test_cases.append(
            LLMTestCase(
                input=item["question"],
                actual_output=item["answer"],
                retrieval_context=list(item["context"])
            )
        )

    model = ChatOpenAI(
        model="llama3-8b-8192",
        temperature = 0,
        base_url = "https://api.groq.com/openai/v1/chat/completions",
        api_key="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",
    )

    # Step 3: Initialize your custom LLM model used for evaluation
    custom_model = EvaluationModel(model=model)

    # Step 4: Define evaluation metrics
    metrics = [
        AnswerRelevancyMetric(model=custom_model, threshold = 0.7, include_reason = True),
        ContextualRelevancyMetric(model=custom_model, threshold = 0.7, include_reason = True),
        FaithfulnessMetric(model=custom_model, threshold = 0.7, include_reason = True)
    ]

    # Step 5: Run the evaluation
    evaluate(test_cases=test_cases, metrics=metrics)

    # Step 6 (Optional): Access individual scores programmatically
    print("\nIndividual Scores:")
    for i, case in enumerate(test_cases):
        print(f"\n--- Test Case {i + 1} ---")
        print("Question:", case.input)
        print("Answer Relevancy:", case.metric_scores["Answer Relevancy"])
        print("Contextual Accuracy:", case.metric_scores["Contextual Accuracy"])
