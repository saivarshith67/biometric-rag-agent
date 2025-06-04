import os
from ..config import DATA_DIR
from langchain_community.document_loaders import PyPDFLoader
from typing import List
from langchain.schema import Document

def load_data() -> List[Document]:
    all_docs : List[Document] = []

    for file in os.listdir(DATA_DIR):
        if file.endswith(".pdf"):
            file_path = os.path.join(DATA_DIR, file)
            loader = PyPDFLoader(file_path)
            docs = loader.load()
            all_docs.extend(docs)
    
    return all_docs


if __name__ == "__main__":
    print(DATA_DIR)