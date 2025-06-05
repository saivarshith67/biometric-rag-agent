from ..data.loader import load_data
from ..data.splitter import split_text

from ..vector_db.embeddings import build_embedding_model
from ..vector_db.vector_store import store_vectors

from .models import build_model
from .tools import build_retriever_tool

from .nodes import (
    generate_answer,
    generate_query_or_respond,
    grade_documents,
    rewrite_question,
)

from .workflow import build_workflow
from .graph_runner import stream_graph_response

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import MessagesState
from functools import partial


class RagPipeline:
    def __init__(self, thread_id: str):
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

    def invoke(self, query: str):
        return stream_graph_response(
            graph=self._graph, query=query, thread_id=self._thread_id
        )
