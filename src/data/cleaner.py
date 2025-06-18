import re
from langchain.schema import Document
from typing import List
from src.utils.logger import get_logger

logger = get_logger(__name__)


def clean_data(documents: List[Document]) -> List[Document]:
    cleaned_docs = []
    for doc in documents:
        text = doc.page_content

        # Remove common page indicators
        text = re.sub(r"(?i)\b(page|pg)[\s:]*\d+\b", "", text)
        # Remove extra newlines
        text = re.sub(r"\n{2,}", "\n", text)
        # Remove extra spaces
        text = re.sub(r"\s{2,}", " ", text)
        # Optionally remove non-ASCII
        # text = re.sub(r"[^\x00-\x7F]+", " ", text)
        # Strip leading/trailing whitespace
        text = text.strip()

        cleaned_docs.append(Document(page_content=text, metadata=doc.metadata))

    logger.info(f"Cleaned {len(documents)} documents successfully.")
    return cleaned_docs
