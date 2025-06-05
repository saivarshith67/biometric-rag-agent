from fastapi import APIRouter, Body, Request
from src.langgraph_agent.rag_pipeline import RagPipeline

router = APIRouter()

@router.post("/query")
def post_query(request : Request,query : str= Body(...)):
    rag_agent = request.app.state.rag_agent
    response = rag_agent.invoke(query)
    return {"message" : response}