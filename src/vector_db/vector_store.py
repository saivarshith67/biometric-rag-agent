from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from typing import List

from src.config import VECTOR_DB_NAME
from src.utils.logger import get_logger

logger = get_logger(__name__)

def store_vectors(
    chunks: List[str],
    embedding_model: HuggingFaceEmbeddings
) -> None:
    vectorstore = Chroma.from_texts(
        texts=chunks,
        embedding=embedding_model,
        persist_directory=VECTOR_DB_NAME
    )
    logger.info(f"Stored the data into Chroma at: {VECTOR_DB_NAME}")


def load_vectorstore(
    embedding_model: HuggingFaceEmbeddings
) -> Chroma:
    vectorstore = Chroma(
        embedding_function=embedding_model,
        persist_directory=VECTOR_DB_NAME
    )
    logger.info(f"Successfully loaded data from Chroma at: {VECTOR_DB_NAME}")
    return vectorstore
