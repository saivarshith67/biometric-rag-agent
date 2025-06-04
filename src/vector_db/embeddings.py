from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from ..config import EMBEDDING_MODEL_NAME

def build_embedding_model() -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)