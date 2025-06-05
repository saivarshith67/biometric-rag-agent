from fastapi import APIRouter, Body
from ...langgraph_agent.rag_pipeline import RagPipeline

router = APIRouter()

@router.post("/query")
def post_query(request : str= Body(...)):
    rag_pipeline = RagPipeline("001")
    response = rag_pipeline.invoke(request)
    return {"message" : response}