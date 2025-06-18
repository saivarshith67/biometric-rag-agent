from src.vector_db.embeddings import build_embedding_model
from src.agent.models import build_model
from src.agent.tools import build_retriever_tool
from src.agent.nodes import (
    generate_answer,
    grade_documents,
    rewrite_question,
    check_query_relevance,
    unrelated_query_response,
    query_relavance_checker,
    initialize_current_query,
    retriever_failed_response,
    generate_tool_call
)
from src.vector_db.vector_store import load_vectorstore
from src.utils.logger import get_logger
from src.agent.workflow import build_workflow
from src.agent.graph_runner import stream_graph_response
from src.agent.response_model import build_response_model
from langgraph.checkpoint.sqlite import SqliteSaver
from functools import partial
from uuid import uuid4
from src.config import DB_URL
import sqlite3

logger = get_logger(__name__)


class RagPipeline:
    def __init__(self, thread_id: uuid4):
        """
        Initialize models and tools, but defer graph creation.
        """
        self._thread_id = thread_id

        # --- Component Initialization ---
        self.embeding_model = build_embedding_model()
        self.vectorstore = load_vectorstore(embedding_model=self.embeding_model)
        self.retriever_tool = build_retriever_tool(vectorstore=self.vectorstore)
        self.response_model = build_response_model(
            retriever_tool=self.retriever_tool
        )
        self.grader_model = build_model()

        # --- Defer connection and graph objects ---
        self.db_connection = None
        self.checkpointer = None
        self._graph = None
        logger.info(f"Pipeline for thread '{self._thread_id}' initialized.")

    def __enter__(self):
        """
        Enter the context: connect to DB, create the checkpointer, and build the graph.
        """
        conn_string = DB_URL
        self.db_connection = sqlite3.connect(conn_string, check_same_thread=False)
        self.checkpointer = SqliteSaver(conn=self.db_connection)

        # --- Wrap node functions ---
        grade_documents_wrapped = partial(
            grade_documents, grader_model=self.grader_model
        )
        rewrite_question_wrapped = partial(
            rewrite_question, response_model=self.response_model
        )
        generate_answer_wrapped = partial(
            generate_answer, response_model=self.response_model
        )
        check_query_relevance_wrapped = partial(
            check_query_relevance, response_model=self.response_model
        )
        unrelated_query_response_wrapped = partial(
            unrelated_query_response, response_model=self.response_model
        )
        query_relavance_checker_wrapped = partial(
            query_relavance_checker, response_model=self.response_model
        )
        
        # ADD THIS: Wrap the generate_tool_call function
        generate_tool_call_wrapped = partial(
            generate_tool_call, 
            response_model=self.response_model,
            retriever_tool=self.retriever_tool
        )

        # --- Build the LangGraph workflow ---
        self._graph = build_workflow(
            retriever_tool=self.retriever_tool,
            rewrite_question=rewrite_question_wrapped,
            generate_answer=generate_answer_wrapped,
            grade_documents=grade_documents_wrapped,
            check_query_relevance=check_query_relevance_wrapped,
            unrelated_query_response=unrelated_query_response_wrapped,
            query_relavance_checker=query_relavance_checker_wrapped,
            initialize_current_query=initialize_current_query,
            retriever_failed_response=retriever_failed_response,
            generate_tool_call=generate_tool_call_wrapped,  # ADD THIS
            checkpointer=self.checkpointer,
        )

        return self

    async def __aenter__(self):
        return self.__enter__()

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Exit the context: automatically close the database connection.
        """
        if self.db_connection:
            self.db_connection.close()
            logger.info("Database connection closed.")

    async def __aexit__(self, exc_type, exc_value, traceback):
        self.__exit__(exc_type, exc_value, traceback)

    def invoke(self, query: str):
        """
        Invoke the graph. The checkpointer will use the thread_id for state.
        """
        if not self._graph:
            raise RuntimeError("RagPipeline must be used within a 'with' block.")

        return stream_graph_response(
            graph=self._graph, query=query, thread_id=self._thread_id
        )