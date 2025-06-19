"""
before running the main.py make sure to run the index_builder.py so that the vector indexes are created
This stuff is moved away from rag_pipeline so as to decrease the startup time

run it with the following command
```python
python -m src.index_builder
```
"""

from src.data.loader import load_data
from src.data.splitter import split_text
from src.data.cleaner import parse_and_clean_pdfs

from src.vector_db.embeddings import build_embedding_model
from src.vector_db.vector_store import store_vectors
from src.utils.logger import get_logger

logger = get_logger(__name__)

def build_indexes() -> None:
    # Step 1: Parse and clean raw PDF files using LlamaParse
    logger.info("Parsing and cleaning raw PDF documents...")
    parse_and_clean_pdfs()

    # Step 2: Load cleaned text documents from cleaned_data/
    logger.info("Loading cleaned documents...")
    all_docs = load_data()

    # Step 3: Split the documents into overlapping chunks
    logger.info("Splitting documents into chunks...")
    chunks = split_text(all_docs)

    # Step 4: Build embeddings and store vectors
    logger.info("Generating embeddings and storing in vector DB...")
    embedding_model = build_embedding_model()
    store_vectors(chunks, embedding_model)

    logger.info("Index building complete.")


if __name__ == "__main__":
    build_indexes()
