from fastapi import APIRouter, Request
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from src.utils.logger import get_logger
from typing import Any
from src.agent.rag_pipeline import RagPipeline
import httpx  # Assuming external APIs like Gemini use httpx or requests

logger = get_logger(__name__)
router = APIRouter()


class QueryRequest(BaseModel):
    query: str


@router.post("/query")
async def post_query(request: Request, query_request: QueryRequest) -> JSONResponse:
    query = query_request.query
    logger.info(f"Hit /query endpoint with query={query}")

    rag_agent: RagPipeline = request.app.state.rag_agent

    try:
        result = rag_agent.invoke(query)  # Synchronous method
        logger.info(f"Successfully processed query: {result}")
        return JSONResponse(
            status_code=200,
            content={"status": "success", "result": result},
        )

    except httpx.HTTPStatusError as http_exc:
        status = http_exc.response.status_code
        detail = http_exc.response.text
        logger.error(f"HTTP error during query: {status} - {detail}")

        return JSONResponse(
            status_code=status,
            content={
                "status": "error",
                "result": "HTTP error while processing query.",
                "details": detail,
            },
        )

    except Exception as e:
        # Specific handling for quota/rate limit errors if the message includes "429"
        if "429" in str(e):
            logger.warning("Rate limit exceeded: suggesting user to retry later.")
            return JSONResponse(
                status_code=429,
                content={
                    "status": "error",
                    "result": "Rate limit exceeded. Please wait and try again.",
                    "help_url": "https://ai.google.dev/gemini-api/docs/rate-limits",
                },
            )

        logger.error(f"Unexpected error processing query: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "result": "Internal server error while processing query.",
                "details": str(e),
            },
        )
