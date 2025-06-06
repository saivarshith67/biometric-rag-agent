from src.config import MODEL_REPO_ID, HF_TOKEN
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from src.utils.logger import get_logger

logger = get_logger(__name__)

def build_model():
    logger.info(f"Creating a hugging face endpoint for the repo id : {MODEL_REPO_ID}")

    hf_endpoint = HuggingFaceEndpoint(
        repo_id=MODEL_REPO_ID,
        task="text-generation",
        max_new_tokens=512,
        do_sample=False,
        repetition_penalty=1.03,
        api_key=HF_TOKEN,
    )

    logger.info("Created an HuggingFaceEndpoint")
    logger.info("Creating an ChatHuggingFace using the endpoint")

    chat_hf = ChatHuggingFace(llm=hf_endpoint, verbose=True, temperature=0)
    
    logger.info("Successfully created the ChatHuggingFace instance")

    return chat_hf

