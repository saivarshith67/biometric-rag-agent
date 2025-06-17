from langchain_google_genai import ChatGoogleGenerativeAI
from src.config import RESPONSE_MODEL_NAME, GOOGLE_API_KEY


def build_response_model(retriever_tool):
    model = ChatGoogleGenerativeAI(
        model=RESPONSE_MODEL_NAME, google_api_key=GOOGLE_API_KEY, temperature=0
    )
    model_with_tool = model.bind_tools(tools=[retriever_tool])
    return model_with_tool
