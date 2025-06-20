from langchain_google_genai import ChatGoogleGenerativeAI
from src.config import RESPONSE_MODEL_NAME, GOOGLE_API_KEY
from langfuse import observe

@observe(as_type="generation")
def build_response_model(retriever_tool, search_tool):
    model = ChatGoogleGenerativeAI(
        model=RESPONSE_MODEL_NAME, google_api_key=GOOGLE_API_KEY, temperature=0
    )
    
    return model
