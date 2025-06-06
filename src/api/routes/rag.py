from fastapi import APIRouter, Body, Request
from src.agent.rag_pipeline import RagPipeline
from src.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()

@router.post("/query")
def post_query(request : Request,query : str= Body(...)):
    logger.info(f"Hit /query endpoint with  query={query}")
    rag_agent = request.app.state.rag_agent
    response = rag_agent.invoke(query)
    logger.info(f"Response from Agent : {response}")
    return {"message" : response}