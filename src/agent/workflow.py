from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.types import Checkpointer
from langgraph.graph import MessagesState
from src.utils.logger import get_logger

logger = get_logger(__name__)


def next_step_after_generate(state: MessagesState) -> str:
    """Route depending on whether the question was rewritten, with loop protection."""
    was_rewritten = state.get("was_rewritten", False)
    rewrite_attempts = state.get("rewrite_attempts", 0)

    if rewrite_attempts >= 2:
        logger.warning("Rewrite attempts exceeded limit of 2")
        return "retrieve"

    return "retrieve" if was_rewritten else "rewrite_question"


def add_nodes(
    workflow: StateGraph,
    retriever_tool,
    check_query_relevance,
    unrelated_query_response,
    generate_query_or_respond,
    rewrite_question,
    generate_answer,
):
    workflow.add_node("check_query_relevance", check_query_relevance)
    workflow.add_node("unrelated_query_response", unrelated_query_response)
    workflow.add_node("generate_query_or_respond", generate_query_or_respond)
    workflow.add_node("retrieve", ToolNode([retriever_tool]))
    workflow.add_node("rewrite_question", rewrite_question)
    workflow.add_node("generate_answer", generate_answer)


def add_edges(workflow: StateGraph, grade_documents, query_relavance_checker):
    workflow.add_edge(START, "check_query_relevance")

    workflow.add_edge("unrelated_query_response", END)

    workflow.add_conditional_edges(
        "check_query_relevance",
        query_relavance_checker,
        {
            "related": "generate_query_or_respond",
            "unrelated": "unrelated_query_response",
        },
    )

    workflow.add_edge("generate_query_or_respond", "rewrite_question")
    workflow.add_edge("rewrite_question", "retrieve")

    workflow.add_conditional_edges(
        "retrieve",
        grade_documents,
        {
            "generate_answer": "generate_answer",
            "rewrite_question": END,
        },
    )
    workflow.add_edge("generate_answer", END)


def build_workflow(
    retriever_tool,
    generate_query_or_respond,
    rewrite_question,
    generate_answer,
    grade_documents,
    check_query_relevance,
    unrelated_query_response,
    query_relavance_checker,
    checkpointer: Checkpointer,
):
    workflow = StateGraph(MessagesState)

    add_nodes(
        workflow,
        retriever_tool,
        check_query_relevance,
        unrelated_query_response,
        generate_query_or_respond,
        rewrite_question,
        generate_answer,
    )

    add_edges(workflow, grade_documents, query_relavance_checker)

    compiled_workflow = workflow.compile(checkpointer=checkpointer).with_config(
        {"merge_next": True}
    )
    compiled_workflow.get_graph().draw_png("./diagrams/graph.png")
    return compiled_workflow
