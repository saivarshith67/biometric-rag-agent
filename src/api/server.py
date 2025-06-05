from fastapi import FastAPI
from src.api.routes import rag
from src.project_setup import project_setup
from src.langgraph_agent.rag_pipeline import RagPipeline
from uuid import uuid4

app = FastAPI()
rag_agent = None

@app.get("/")
def root():
    project_setup()
    thread_id = uuid4()
    app.state.rag_agent = RagPipeline(thread_id=thread_id)
    return {"message" : "Welcome to biometric rag agent and Rag Agent is initialised"}

app.include_router(rag.router)