import os
from src.config import DATA_DIR
from langchain_community.document_loaders import PyPDFLoader
from typing import List
from langchain.schema import Document
from src.utils.logger import get_logger

logger = get_logger(__name__)

def load_data() -> List[Document]:
    all_docs : List[Document] = []
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    data_directory = os.path.join(base_dir, DATA_DIR)

    logger.info(f"Extracting data from : {data_directory}")

    for file in os.listdir(data_directory):
        if file.endswith(".pdf"):
            file_path = os.path.join(data_directory, file)
            loader = PyPDFLoader(file_path)
            docs = loader.load()
            all_docs.extend(docs)
    
    logger.info("Extracted Data completely")
    
    return all_docs

