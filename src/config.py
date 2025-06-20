from dotenv import load_dotenv
import os

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

DATA_DIR = "data"

EMBEDDING_MODEL_NAME = "BAAI/bge-small-en-v1.5"

VECTOR_DB_NAME = "chroma_vector_db"

MODEL_REPO_ID = "meta-llama/Llama-4-Maverick-17B-128E-Instruct"

DB_URL = os.getenv("DB_URL")

RESPONSE_MODEL_NAME = "gemini-2.5-flash-lite-preview-06-17"

LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY")

LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY")

LANGFUSE_HOST_URL = os.getenv("LANGFUSE_HOST_URL")
