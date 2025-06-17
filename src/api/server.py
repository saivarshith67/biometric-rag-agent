from fastapi import FastAPI
from src.api.routes import query
from src.project_setup import project_setup
from src.agent.rag_pipeline import RagPipeline
from src.utils.logger import get_logger
from uuid import uuid4
from contextlib import asynccontextmanager

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting FastAPI application...")
    project_setup()
    logger.info("Project setup completed")

    # Proper async context usage
    rag_pipeline = RagPipeline(thread_id=uuid4())
    app.state._rag_pipeline_context = rag_pipeline  # Keep reference for manual closing
    app.state.rag_agent = await rag_pipeline.__aenter__()
    logger.info("RagPipeline initialized")
    logger.info("APPLICATION STARTUP COMPLETED")
    logger.info(f"{app.state.rag_agent}")

    yield  # Run app

    logger.info("Shutting down RagPipeline...")
    await app.state._rag_pipeline_context.__aexit__(None, None, None)
    logger.info("RagPipeline shut down")


app = FastAPI(lifespan=lifespan)


@app.get("/")
def root():
    return {"message": "Welcome to biometric rag agent"}


app.include_router(query.router)
