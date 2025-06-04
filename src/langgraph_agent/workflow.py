from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from typing import Callable, Dict

def add_nodes(workflow: StateGraph, retriever_tool, generate_query_or_respond: Callable, 
              rewrite_question: Callable, generate_answer: Callable):
    workflow.add_node(generate_query_or_respond)
    workflow.add_node("retrieve", ToolNode([retriever_tool]))
    workflow.add_node(rewrite_question)
    workflow.add_node(generate_answer)

def add_edges(workflow: StateGraph, grade_documents: Callable):
    workflow.add_edge(START, "generate_query_or_respond")
    
    workflow.add_conditional_edges(
        "generate_query_or_respond",
        tools_condition,
        {
            "tools": "retrieve",
            END: END,
        },
    )

    workflow.add_conditional_edges("retrieve", grade_documents)
    workflow.add_edge("generate_answer", END)
    workflow.add_edge("rewrite_question", "generate_query_or_respond")

def build_workflow(
    MessagesState,
    retriever_tool,
    generate_query_or_respond: Callable,
    rewrite_question: Callable,
    generate_answer: Callable,
    grade_documents: Callable,
    memory_saver=None,
):
    workflow = StateGraph(MessagesState)
    add_nodes(workflow, retriever_tool, generate_query_or_respond, rewrite_question, generate_answer)
    add_edges(workflow, grade_documents)

    memory = memory_saver
    return workflow.compile(checkpointer=memory)
