from src.evaluator.qa_pairs import qa_pairs
from src.evaluator.prompts import (
    question_relevance_critique_prompt,
    question_standalone_critique_prompt,
    question_groundedness_critique_prompt,
)
import pandas as pd
from tqdm import tqdm
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from src.config import MODEL_REPO_ID
import time


def qa_critique():
    hf_endpoint = HuggingFaceEndpoint(
        repo_id=MODEL_REPO_ID,
        task="text-generation",
        max_new_tokens=50,
        do_sample=False,
        repetition_penalty=1.03,
    )

    chat_hf = ChatHuggingFace(llm=hf_endpoint, verbose=True, temperature=0)

    # Prepare a list to hold updated outputs
    updated_outputs = []

    for output in tqdm(qa_pairs):
        try:
            evaluations = {
                "groundedness": chat_hf.invoke(
                    question_groundedness_critique_prompt.format(
                        context=output["context"], question=output["question"]
                    ),
                ),
                "relevance": chat_hf.invoke(
                    question_relevance_critique_prompt.format(
                        question=output["question"]
                    ),
                ),
                "standalone": chat_hf.invoke(
                    question_standalone_critique_prompt.format(
                        question=output["question"]
                    ),
                ),
            }

            for criterion, evaluation in evaluations.items():
                score = int(evaluation.split("Total rating: ")[-1].strip())
                eval_text = (
                    evaluation.split("Total rating: ")[-2]
                    .split("Evaluation: ")[1]
                    .strip()
                )
                output[f"{criterion}_score"] = score
                output[f"{criterion}_eval"] = eval_text

        except Exception as e:
            output["error"] = str(e)
            continue

        updated_outputs.append(output)

        time.sleep(60)

    df = pd.DataFrame(updated_outputs)
    df.to_csv("qa_critique.csv", index=False)
    print("Saved all critiques to qa_critique.csv")


if __name__ == "__main__":
    qa_critique()
