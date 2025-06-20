# src.agent.workflow - FIXED VERSION

from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.types import Checkpointer
from src.agent.state import State
from src.utils.logger import get_logger

logger = get_logger(__name__)


def next_step_after_generate(state: State) -> str:
    """Route depending on whether the question was rewritten, with loop protection."""
    was_rewritten = state.get("was_rewritten", False)
    rewrite_attempts = state.get("rewrite_attempts", 0)

    if rewrite_attempts >= 2:
        logger.warning("Rewrite attempts exceeded limit of 2")
        return "generate_retriever_tool_call"  # Generate tool calls first

    return "generate_retriever_tool_call" if was_rewritten else "rewrite_question"


def add_nodes(
    workflow: StateGraph,
    retriever_tool,
    search_tool,
    check_query_relevance,
    unrelated_query_response,
    rewrite_question,
    generate_answer,
    initialize_current_query,
    generate_web_search_tool_call,
    generate_retriever_tool_call,  # Add this parameter
):
    workflow.add_node("initialize_current_query", initialize_current_query)
    workflow.add_node("check_query_relevance", check_query_relevance)
    workflow.add_node("unrelated_query_response", unrelated_query_response)
    workflow.add_node(
        "generate_retriever_tool_call", generate_retriever_tool_call
    )  # Add this node
    workflow.add_node("retrieve", ToolNode([retriever_tool]))
    workflow.add_node("web_search", ToolNode([search_tool]))
    workflow.add_node("rewrite_question", rewrite_question)
    workflow.add_node("generate_answer", generate_answer)
    workflow.add_node("generate_web_search_tool_call", generate_web_search_tool_call)


def add_edges(workflow: StateGraph, grade_documents, query_relavance_checker):
    workflow.add_edge(START, "initialize_current_query")

    workflow.add_edge("initialize_current_query", "check_query_relevance")

    workflow.add_edge("unrelated_query_response", END)

    workflow.add_conditional_edges(
        "check_query_relevance",
        query_relavance_checker,
        {
            "related": "rewrite_question",
            "unrelated": "unrelated_query_response",
        },
    )

    # CHANGED: After rewrite, go to generate_retriever_tool_call to create tool calls
    workflow.add_edge("rewrite_question", "generate_retriever_tool_call")

    # CHANGED: From generate_retriever_tool_call, go to retrieve
    workflow.add_edge("generate_retriever_tool_call", "retrieve")

    # workflow.add_conditional_edges(
    #     "retrieve",
    #     grade_documents,
    #     {
    #         "generate_answer": "generate_answer",
    #         "rewrite_question": "generate_web_search_tool_call",
    #         # rewriting means retriever failed to retrieve relevant docs so directly going to this node
    #     },
    # )

    workflow.add_edge("retrieve", "generate_web_search_tool_call")
    workflow.add_edge("generate_web_search_tool_call", "web_search")
    workflow.add_edge("web_search", "generate_answer")
    workflow.add_edge("generate_answer", END)


def build_workflow(
    retriever_tool,
    search_tool,
    rewrite_question,
    generate_answer,
    grade_documents,
    check_query_relevance,
    unrelated_query_response,
    query_relavance_checker,
    initialize_current_query,
    checkpointer: Checkpointer,
    generate_web_search_tool_call,
    generate_retriever_tool_call,  # Add this parameter
):
    workflow = StateGraph(State)

    add_nodes(
        workflow,
        retriever_tool,
        search_tool,
        check_query_relevance,
        unrelated_query_response,
        rewrite_question,
        generate_answer,
        initialize_current_query,
        generate_web_search_tool_call,
        generate_retriever_tool_call,  # Pass it to add_nodes
    )

    add_edges(workflow, grade_documents, query_relavance_checker)

    compiled_workflow = workflow.compile(checkpointer=checkpointer)
    compiled_workflow.get_graph().draw_png("./diagrams/graph.png")
    return compiled_workflow
