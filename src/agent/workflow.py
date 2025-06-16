from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.types import Checkpointer
from langgraph.graph import MessagesState
from src.utils.logger import get_logger
from typing import Literal

logger = get_logger(__name__)


def next_step_after_generate(state: MessagesState) -> str:
    """Route depending on whether the question was rewritten, with loop protection."""
    was_rewritten = state.get("was_rewritten", False)
    rewrite_attempts = state.get("rewrite_attempts", 0)

    if rewrite_attempts >= 2:
        logger.warning("Rewrite attemps exceeded limit of 2")
        return "retrieve"

    if was_rewritten:
        return "retrieve"
    else:
        return "rewrite_question"


def add_nodes(
    workflow: StateGraph,
    retriever_tool,
    generate_query_or_respond,
    rewrite_question,
    generate_answer,
):
    workflow.add_node("generate_query_or_respond", generate_query_or_respond)
    workflow.add_node("retrieve", ToolNode([retriever_tool]))
    workflow.add_node("rewrite_question", rewrite_question)
    workflow.add_node("generate_answer", generate_answer)


def add_edges(workflow: StateGraph, grade_documents):
    workflow.add_edge(START, "generate_query_or_respond")

    workflow.add_edge(
        "generate_query_or_respond",
        "rewrite_question",
    )
    workflow.add_edge("rewrite_question", "retrieve")  # Directly go to retrieve

    workflow.add_conditional_edges(
        "retrieve",
        grade_documents,
        {
            "generate_answer": "generate_answer",
            "rewrite_question": "rewrite_question",
        },
    )
    workflow.add_edge("generate_answer", END)


def build_workflow(
    retriever_tool,
    generate_query_or_respond,
    rewrite_question,
    generate_answer,
    grade_documents,
    checkpointer: Checkpointer,
):
    workflow = StateGraph(MessagesState)

    add_nodes(
        workflow,
        retriever_tool,
        generate_query_or_respond,
        rewrite_question,
        generate_answer,
    )

    add_edges(workflow, grade_documents)

    compiled_workflow = workflow.compile(checkpointer=checkpointer)
    compiled_workflow.get_graph().draw_png(".graph.png")
    return compiled_workflow
