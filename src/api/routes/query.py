from fastapi import APIRouter, Request
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from src.utils.logger import get_logger
from typing import Any

logger = get_logger(__name__)
router = APIRouter()


class QueryRequest(BaseModel):
    query: str


@router.post("/query")
async def post_query(request: Request, query_request: QueryRequest) -> JSONResponse:
    query = query_request.query
    logger.info(f"Hit /query endpoint with query={query}")

    rag_agent = request.app.state.rag_agent

    try:
        result = rag_agent.invoke(query)  # No await — your `invoke()` is sync
        logger.info(f"Successfully processed query: {result}")
        return JSONResponse(
            status_code=200, content={"status": "success", "result": result}
        )
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        return JSONResponse(
            status_code=400, content={"status": "error", "message": str(e)}
        )
