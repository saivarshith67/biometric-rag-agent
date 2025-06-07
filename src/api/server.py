from fastapi import FastAPI
from src.api.routes import query
from src.project_setup import project_setup
from src.agent.rag_pipeline import RagPipeline
from src.utils.logger import get_logger
from uuid import uuid4

app = FastAPI()
logger = get_logger(__name__)
rag_agent = None

@app.get("/")
def root():
    logger.info("Root endpoint hit")
    project_setup()
    logger.info("Project set up completed")
    thread_id = uuid4()
    app.state.rag_agent = RagPipeline(thread_id=thread_id)
    logger.info("Rag Agent initialised")
    return {"message" : "Welcome to biometric rag agent and Rag Agent is initialised"}

app.include_router(query.router)