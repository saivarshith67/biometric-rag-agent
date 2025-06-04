from dotenv import load_dotenv
import os

load_dotenv()

HF_TOKEN = os.getenv("HUGGINGFACE_ACCESS_TOKEN")

DATA_DIR = ".../data"

EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


VECTOR_DB_NAME = "my_faiss_index"

MODEL_REPO_ID = "meta-llama/Llama-4-Maverick-17B-128E-Instruct"
