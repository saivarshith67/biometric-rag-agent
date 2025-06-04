from huggingface_hub import login
from .config import HF_TOKEN

def project_setup() -> None:
    login(token=HF_TOKEN)