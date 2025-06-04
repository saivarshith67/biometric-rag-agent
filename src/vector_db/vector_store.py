from langchain_community.vectorstores import FAISS
from ..config import VECTOR_DB_NAME
from langchain_huggingface import HuggingFaceEmbeddings
from typing import List

def store_vectors(chunks: List[str], 
                  embedding_model: HuggingFaceEmbeddings
                  ):
    vectorstore = FAISS.from_texts(texts=chunks, embedding=embedding_model)
    vectorstore.save_local(VECTOR_DB_NAME)
