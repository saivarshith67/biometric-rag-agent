from src.config import RESPONSE_MODEL_NAME, GOOGLE_API_KEY
from langchain_google_genai import ChatGoogleGenerativeAI
from src.utils.logger import get_logger

logger = get_logger(__name__)


def build_model():
    llm = ChatGoogleGenerativeAI(
        model=RESPONSE_MODEL_NAME, google_api_key=GOOGLE_API_KEY, temperature=0
    )

    logger.info("Succesfully created an instance of LLM")

    return llm
