from fastapi import APIRouter, Request
from pydantic import BaseModel
from src.utils.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()

# Request model
class QueryRequest(BaseModel):
    query: str

@router.post("/query")
def post_query(request: Request, query_request: QueryRequest):
    query = query_request.query
    logger.info(f"Hit /query endpoint with query={query}")
    rag_agent = request.app.state.rag_agent
    response = rag_agent.invoke(query)
    logger.info(f"Response from Agent: {response}")
    return {"message": response}
