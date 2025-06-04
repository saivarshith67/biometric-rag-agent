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
from functools import partial

from langgraph.graph import MessagesState
from langgraph.checkpoint.memory import MemorySaver


def main() -> None:
    # setup the project
    project_setup()

    all_docs = load_data()
    chunks = split_text(all_docs=all_docs)

    embedding_model = build_embedding_model()
    vectorstore = store_vectors(chunks, embedding_model)

    response_model = build_model()
    grader_model = build_model()
    retriever_tool = build_retriever_tool(vectorstore=vectorstore)
    memory = MemorySaver()

    gen_query_or_respond_wrapped = partial(
        generate_query_or_respond,
        response_model=response_model,
        retriever_tool=retriever_tool,
    )
    grade_documents_wrapped = partial(grade_documents, grader_model=grader_model)
    rewrite_question_wrapped = partial(rewrite_question, response_model=response_model)
    generate_answer_wrapped = partial(generate_answer, response_model=response_model)

    graph = build_workflow(
        MessagesState,
        retriever_tool,
        gen_query_or_respond_wrapped,
        rewrite_question_wrapped,
        generate_answer_wrapped,
        grade_documents_wrapped,
        memory_saver=memory,
    )

    stream_graph_response(graph, "Hi My name is sai", "001")
    stream_graph_response(graph, "How to create a user?", "001")
    stream_graph_response(graph, "Do you remember my name?", "001")
    stream_graph_response(graph, "What is the appropriate frequency for camera?", "001")


if __name__ == "__main__":
    main()
