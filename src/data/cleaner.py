## src.data.cleaner

import os
from llama_parse import LlamaParse
from src.config import DATA_DIR
from langchain.schema import Document
from typing import List
from src.utils.logger import get_logger

logger = get_logger(__name__)
CLEANED_DIR = "cleaned_data"


def parse_and_clean_pdfs() -> None:
    os.makedirs(CLEANED_DIR, exist_ok=True)
    parser = LlamaParse(result_type="markdown")  # Structured markdown output

    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    data_directory = os.path.join(base_dir, DATA_DIR)
    output_directory = os.path.join(base_dir, CLEANED_DIR)

    logger.info(f"Parsing and cleaning PDFs from {data_directory}")

    for file in os.listdir(data_directory):
        if file.endswith(".pdf"):
            file_path = os.path.join(data_directory, file)
            docs = parser.load_data(file_path)
            for idx, doc in enumerate(docs):
                output_path = os.path.join(
                    output_directory, f"{os.path.splitext(file)[0]}_part{idx}.txt"
                )
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(doc.text.strip())

    logger.info(f"Cleaned documents stored at: {output_directory}")
