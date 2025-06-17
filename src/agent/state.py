from typing import Optional, Literal, Annotated, TypedDict
from langgraph.graph import add_messages
from langchain_core.messages import AnyMessage


class State(TypedDict):
    """
    Custom state extending LangGraph's MessagesState with additional fields
    needed for query routing and control.
    """
    messages: Annotated[list[AnyMessage], add_messages]
    rewrite_attempts: int
    was_rewritten: bool
    context_docs: Optional[str]
    relevance: Optional[Literal["related", "unrelated"]]
    current_query: Optional[str]
