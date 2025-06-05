import os
from src.config import DATA_DIR
from langchain_community.document_loaders import PyPDFLoader
from typing import List
from langchain.schema import Document
from src.utils.logger import get_logger

logger = get_logger(__name__)

def load_data() -> List[Document]:
    all_docs : List[Document] = []
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    DATA_DIRECTORY = os.path.join(BASE_DIR, DATA_DIR)

    logger.info(f"Extracting data from : {DATA_DIRECTORY}")

    for file in os.listdir(DATA_DIRECTORY):
        if file.endswith(".pdf"):
            file_path = os.path.join(DATA_DIRECTORY, file)
            loader = PyPDFLoader(file_path)
            docs = loader.load()
            all_docs.extend(docs)
    
    logger.info("Extracted Data completely")
    
    return all_docs

