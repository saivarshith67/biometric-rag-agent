from huggingface_hub import login
from .config import HF_TOKEN, DB_URL

def project_setup() -> None:
    if not HF_TOKEN:
        raise ValueError("HUGGINGFACE_ACCESS_TOKEN is not set. Please set it in your environment variables.")

    if not DB_URL:
        raise ValueError("DB_URL is not set. Please set it in your environment variables.")
        
    login(token=HF_TOKEN)