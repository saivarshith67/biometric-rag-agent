import re
from langchain.schema import Document
from typing import List
from src.utils.logger import get_logger

logger = get_logger(__name__)


def clean_data(documents: List[Document]) -> List[Document]:
    cleaned_docs = []
    for doc in documents:
        text = doc.page_content

        # Cleaning steps
        text = re.sub(r"(?i)page \d+", "", text)
        text = re.sub(r"\n{2,}", "\n", text)
        text = re.sub(r"\s{2,}", " ", text)

        cleaned_docs.append(Document(page_content=text.strip(), metadata=doc.metadata))
    logger.info("Cleaned the documents successfully")
    return cleaned_docs
