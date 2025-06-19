import os
from typing import List
from langchain.schema import Document
from src.utils.logger import get_logger

logger = get_logger(__name__)
CLEANED_DIR = "cleaned_data"

def load_data() -> List[Document]:
    all_docs: List[Document] = []
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    cleaned_directory = os.path.join(base_dir, CLEANED_DIR)

    logger.info(f"Loading cleaned text documents from : {cleaned_directory}")

    for file in os.listdir(cleaned_directory):
        if file.endswith(".txt"):
            file_path = os.path.join(cleaned_directory, file)
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                all_docs.append(Document(page_content=content, metadata={"source": file}))

    logger.info("Loaded cleaned data completely")
    return all_docs