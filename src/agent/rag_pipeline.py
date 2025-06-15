from src.vector_db.embeddings import build_embedding_model
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
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import MessagesState
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
        self.response_model = build_model()
        self.grader_model = build_model()
        self.retriever_tool = build_retriever_tool(vectorstore=self.vectorstore)

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

        gen_query_or_respond_wrapped = partial(
            generate_query_or_respond,
            response_model=self.response_model,
            retriever_tool=self.retriever_tool,
        )
        grade_documents_wrapped = partial(
            grade_documents, grader_model=self.grader_model
        )
        rewrite_question_wrapped = partial(
            rewrite_question, response_model=self.response_model
        )
        generate_answer_wrapped = partial(
            generate_answer, response_model=self.response_model
        )

        self._graph = build_workflow(
            retriever_tool=self.retriever_tool,
            generate_query_or_respond=gen_query_or_respond_wrapped,
            rewrite_question=rewrite_question_wrapped,
            generate_answer=generate_answer_wrapped,
            grade_documents=grade_documents_wrapped,
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
