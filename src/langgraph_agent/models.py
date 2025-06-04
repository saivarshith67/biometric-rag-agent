from ..config import MODEL_REPO_ID, HF_TOKEN
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace


def build_model():
    hf_endpoint = HuggingFaceEndpoint(
        repo_id=MODEL_REPO_ID,
        task="text-generation",
        max_new_tokens=512,
        do_sample=False,
        repetition_penalty=1.03,
        api_key=HF_TOKEN,
    )

    return ChatHuggingFace(llm=hf_endpoint, verbose=True, temperature=0)


