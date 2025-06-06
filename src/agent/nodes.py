from langgraph.graph import MessagesState
from pydantic import BaseModel, Field
from src.agent.prompts import GRADE_PROMPT, REWRITE_PROMPT, GENERATE_PROMPT
from typing import Literal

class GradeDocuments(BaseModel):
    """Grade documents using a binary score for relevance check."""

    binary_score: str = Field(
        description="Relevance score: 'yes' if relevant, or 'no' if not relevant"
    )


def generate_query_or_respond(state: MessagesState, response_model, retriever_tool):
    response = response_model.bind_tools(
        tools=[retriever_tool]
    ).invoke(state["messages"])

    return {"messages" : [response]}

def grade_documents(
    state: MessagesState,
    grader_model
) -> Literal["generate_answer", "rewrite_question"]:
    """Determine whether the retrieved documents are relevant to the question."""
    question = state["messages"][0].content
    context = state["messages"][-1].content

    prompt = GRADE_PROMPT.format(question=question, context=context)
    response = grader_model.invoke(
        [{"role": "user", "content": prompt}]
    )

    answer = response.content.strip().lower()

    # crude check for binary response
    if "yes" in answer:
        return "generate_answer"
    else:
        return "rewrite_question"



def rewrite_question(state: MessagesState, response_model):
    """Rewrite the original user question."""
    messages = state["messages"]
    question = messages[0].content
    prompt = REWRITE_PROMPT.format(question=question)
    response = response_model.invoke([{"role": "user", "content": prompt}])
    return {"messages": [{"role": "user", "content": response.content}]}


def generate_answer(state: MessagesState, response_model):
    """Generate an answer."""
    question = state["messages"][0].content
    context = state["messages"][-1].content
    prompt = GENERATE_PROMPT.format(question=question, context=context)
    response = response_model.invoke([{"role": "user", "content": prompt}])
    return {"messages": [response]}