from .project_setup import project_setup
from .data.loader import load_data
from .data.splitter import split_text

from .vector_db.embeddings import build_embedding_model
from .vector_db.vector_store import store_vectors

from .langgraph_agent.graph_runner import stream_graph_response
from .langgraph_agent.workflow import build_workflow
from .langgraph_agent.models import build_model
from .langgraph_agent.tools import build_retriever_tool
from .langgraph_agent.nodes import (
    generate_answer,
    generate_query_or_respond,
    grade_documents,
    rewrite_question,
)

from .langgraph_agent.rag_pipeline import RagPipeline
from functools import partial

from langgraph.graph import MessagesState
from langgraph.checkpoint.memory import MemorySaver


def main() -> None:
    # setup the project
    project_setup()

    rag_pipeline = RagPipeline("001")
    response = rag_pipeline.invoke("Hi My name is sai")
    print(f"AI : {response}")
    response = rag_pipeline.invoke("How to create a user?")
    print(f"AI : {response}")
    response = rag_pipeline.invoke(
        "Do you remember my name? if so please tell me my name"
    )
    print(f"AI : {response}")
    response = rag_pipeline.invoke("What is the perfect frequency for the camera?")
    print(f"AI : {response}")


if __name__ == "__main__":
    main()
