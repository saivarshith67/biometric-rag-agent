""" 
before running the main.py make sure to run the index_builder.py so that the vector indexes are created
This stuff is moved away from rag_pipeline so as to increase the startup time

run it with the following command
```python
python -m src.index_builder
```
"""

from src.data.loader import load_data
from src.data.splitter import split_text

from src.vector_db.embeddings import build_embedding_model
from src.vector_db.vector_store import store_vectors

def build_indexes() -> None:
    all_docs = load_data()
    chunks = split_text(all_docs=all_docs)
    embedding_model = build_embedding_model()
    store_vectors(chunks, embedding_model)
    pass



if __name__ == "__main__":
    build_indexes()