from tqdm import tqdm
import random
from src.data.loader import load_data
from src.data.splitter import split_text
from langchain_openai import ChatOpenAI


def qa_generator():



    chat = ChatOpenAI(
        api_key="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",
        base_url="https://openrouter.ai/api/v1",
        model="mistralai/devstral-small:free"
    )

    QA_generation_prompt = """
    Your task is to write a factoid question and an answer given a context.
    Your factoid question should be answerable with a specific, concise piece of factual information from the context.
    Your factoid question should be formulated in the same style as questions users could ask in a search engine.
    This means that your factoid question MUST NOT mention something like "according to the passage" or "context".

    Provide your answer as follows:

    Output:::
    Factoid question: (your factoid question)
    Answer: (your answer to the factoid question)

    Now here is the context.

    Context: {context}\n
    Output:::"""


    N_GENERATIONS = 10  # We intentionally generate only 10 QA couples here for cost and time considerations

    print(f"Generating {N_GENERATIONS} QA couples...")
    docs = load_data()
    docs_processed = split_text(docs)

    


    outputs = []
    for sampled_context in tqdm(random.sample(docs_processed, N_GENERATIONS)):
        # Generate QA couple
        output_QA_couple = chat.invoke(QA_generation_prompt.format(context=sampled_context))
        try:
            question = output_QA_couple.split("Factoid question: ")[-1].split("Answer: ")[0]
            answer = output_QA_couple.split("Answer: ")[-1]
            assert len(answer) < 300, "Answer is too long"
            outputs.append(
                {
                    "context": sampled_context.page_content,
                    "question": question,
                    "answer": answer,
                    "source_doc": sampled_context.metadata["source"],
                }
            )
        except:
            continue

    question_groundedness_critique_prompt = """
    You will be given a context and a question.
    Your task is to provide a 'total rating' scoring how well one can answer the given question unambiguously with the given context.
    Give your answer on a scale of 1 to 5, where 1 means that the question is not answerable at all given the context, and 5 means that the question is clearly and unambiguously answerable with the context.

    Provide your answer as follows:

    Answer:::
    Evaluation: (your rationale for the rating, as a text)
    Total rating: (your rating, as a number between 1 and 5)

    You MUST provide values for 'Evaluation:' and 'Total rating:' in your answer.

    Now here are the question and context.

    Question: {question}\n
    Context: {context}\n
    Answer::: """

    question_relevance_critique_prompt = """
    You will be given a question.
    Your task is to provide a 'total rating' representing how useful this question can be to machine learning developers building NLP applications with the Hugging Face ecosystem.
    Give your answer on a scale of 1 to 5, where 1 means that the question is not useful at all, and 5 means that the question is extremely useful.

    Provide your answer as follows:

    Answer:::
    Evaluation: (your rationale for the rating, as a text)
    Total rating: (your rating, as a number between 1 and 5)

    You MUST provide values for 'Evaluation:' and 'Total rating:' in your answer.

    Now here is the question.

    Question: {question}\n
    Answer::: """

    question_standalone_critique_prompt = """
    You will be given a question.
    Your task is to provide a 'total rating' representing how context-independent this question is.
    Give your answer on a scale of 1 to 5, where 1 means that the question depends on additional information to be understood, and 5 means that the question makes sense by itself.
    For instance, if the question refers to a particular setting, like 'in the context' or 'in the document', the rating must be 1.
    The questions can contain obscure technical nouns or acronyms like Gradio, Hub, Hugging Face or Space and still be a 5: it must simply be clear to an operator with access to documentation what the question is about.

    For instance, "What is the name of the checkpoint from which the ViT model is imported?" should receive a 1, since there is an implicit mention of a context, thus the question is not independent from the context.

    Provide your answer as follows:

    Answer:::
    Evaluation: (your rationale for the rating, as a text)
    Total rating: (your rating, as a number between 1 and 5)

    You MUST provide values for 'Evaluation:' and 'Total rating:' in your answer.

    Now here is the question.

    Question: {question}\n
    Answer::: """


    print("Generating critique for each QA couple...")

    for output in tqdm(outputs):
        evaluations = {
            "groundedness": chat.invoke(
                question_groundedness_critique_prompt.format(context=output["context"], question=output["question"]),
            ),
            "relevance": chat.invoke(
                question_relevance_critique_prompt.format(question=output["question"]),
            ),
            "standalone": chat.invoke(
                question_standalone_critique_prompt.format(question=output["question"]),
            ),
        }
        try:
            for criterion, evaluation in evaluations.items():
                score, eval = (
                    int(evaluation.split("Total rating: ")[-1].strip()),
                    evaluation.split("Total rating: ")[-2].split("Evaluation: ")[1],
                )
                output.update(
                    {
                        f"{criterion}_score": score,
                        f"{criterion}_eval": eval,
                    }
                )
        except Exception as e:
            print(e)
            continue

    print(outputs)

        
if __name__ == "__main__":
    qa_generator()