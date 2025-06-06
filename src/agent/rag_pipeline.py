from src.data.loader import load_data
from src.data.splitter import split_text

from src.vector_db.embeddings import build_embedding_model
from src.vector_db.vector_store import store_vectors

from src.agent.models import build_model
from src.agent.tools import build_retriever_tool

from src.agent.nodes import (
    generate_answer,
    generate_query_or_respond,
    grade_documents,
    rewrite_question,
)

from src.vector_db.vector_store import load_vectorstore
from src.utils.logger import get_logger
from src.agent.workflow import build_workflow
from src.agent.graph_runner import stream_graph_response
from src.agent.memory import get_memory

from langgraph.graph import MessagesState
from functools import partial
from uuid import uuid4

logger = get_logger(__name__)

class RagPipeline:
    def __init__(self, thread_id: uuid4):
        
        embeding_model = build_embedding_model()
        vectorstore = load_vectorstore(embedding_model=embeding_model)
        response_model = build_model()
        grader_model = build_model()
        retriever_tool = build_retriever_tool(vectorstore=vectorstore)
        memory = get_memory()

        gen_query_or_respond_wrapped = partial(
            generate_query_or_respond,
            response_model=response_model,
            retriever_tool=retriever_tool,
        )
        grade_documents_wrapped = partial(grade_documents, grader_model=grader_model)
        rewrite_question_wrapped = partial(
            rewrite_question, response_model=response_model
        )
        generate_answer_wrapped = partial(
            generate_answer, response_model=response_model
        )

        self._thread_id = thread_id

        self._graph = build_workflow(
            MessagesState,
            retriever_tool,
            gen_query_or_respond_wrapped,
            rewrite_question_wrapped,
            generate_answer_wrapped,
            grade_documents_wrapped,
            memory_saver=memory,
        )

        logger.info("Successfully initiated the rag pipeline")


    def invoke(self, query: str):
        return stream_graph_response(
            graph=self._graph, query=query, thread_id=self._thread_id
        )
