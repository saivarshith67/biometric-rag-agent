from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List
from langchain.schema import Document
from src.utils.logger import get_logger

logger = get_logger(__name__)


def split_text(cleaned_docs: List[Document]) -> List[Document]:
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500, chunk_overlap=100
    )

    # Split and retain metadata
    split_docs = text_splitter.split_documents(cleaned_docs)

    logger.info(f"Total chunks created: {len(split_docs)}")
    return split_docs
