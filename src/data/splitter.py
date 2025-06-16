from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List
from langchain.schema import Document
from src.utils.logger import get_logger

logger = get_logger(__name__)

def split_text(all_docs: List[Document]) -> List[str]:
    # Initialize the text splitter
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    
    texts: List[str] = []
    for doc in all_docs:
        texts.append(doc.page_content)
    
    chunks: List[str] = []
    for text in texts:
        split_chunks = text_splitter.split_text(text)
        for chunk in split_chunks:
            chunks.append(chunk)

    logger.info(f"Total chunks created: {len(chunks)}")
    return chunks
