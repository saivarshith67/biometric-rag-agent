from langgraph.graph import MessagesState
from pydantic import BaseModel, Field
from typing import Literal
from langchain.output_parsers import BooleanOutputParser
from langchain.output_parsers.retry import RetryWithErrorOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

from src.agent.prompts import GRADE_PROMPT, REWRITE_PROMPT, GENERATE_PROMPT
from src.utils.logger import get_logger

logger = get_logger(__name__)

class GradeDocuments(BaseModel):
    """Grade documents using a binary score for relevance check."""
    binary_score: str = Field(
        description="Relevance score: 'yes' if relevant, or 'no' if not relevant"
    )

def _clean_context(raw_text: str) -> str:
    """Clean up duplicated lines and excessive whitespace from retrieved context."""
    lines = raw_text.splitlines()
    unique_lines = list(dict.fromkeys(line.strip() for line in lines if line.strip()))
    return "\n".join(unique_lines)

def generate_query_or_respond(state: MessagesState, response_model, retriever_tool):
    response = response_model.bind_tools(
        tools=[retriever_tool]
    ).invoke(state["messages"], tool_choice="auto")

    return {"messages": [response]}


def _get_latest_user_question(messages):
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            return msg.content
    raise ValueError("No user message found in the state.")


def _get_latest_context(messages):
    for msg in reversed(messages):
        if isinstance(msg, (AIMessage, ToolMessage)):  # or SystemMessage
            return msg.content
    raise ValueError("No context message found in the state.")


def grade_documents(
    state: MessagesState,
    grader_model
) -> Literal["generate_answer", "rewrite_question"]:
    """Determine whether the retrieved documents are relevant to the question."""

    question = _get_latest_user_question(state["messages"])
    context = _get_latest_context(state["messages"])

    prompt_template = PromptTemplate.from_template(GRADE_PROMPT)
    parser = BooleanOutputParser()
    retrying_parser = RetryWithErrorOutputParser.from_llm(
        llm=grader_model,
        parser=parser,
        prompt=prompt_template,
        max_retries=1,
    )

    input_values = {"question": question, "context": context}
    prompt_value = prompt_template.format_prompt(**input_values)
    raw_output = grader_model.invoke(prompt_value)

    try:
        result = retrying_parser.parse_with_prompt(
            completion=raw_output.content,
            prompt_value=prompt_value,
        )
    except Exception as e:
        print(f"Parser failed: {e}")
        return "rewrite_question"

    return "generate_answer" if result else "rewrite_question"


def rewrite_question(state: MessagesState, response_model):
    """Rewrite the latest user question and flag the state."""
    messages = state["messages"]
    question = _get_latest_user_question(messages)
    prompt = REWRITE_PROMPT.format(question=question)

    response = response_model.invoke([HumanMessage(content=prompt)])
    logger.debug(f"Rewrite response: {response}")

    # Replace the latest user question with the rewritten question
    new_messages = messages[:]
    for i in reversed(range(len(messages))):
        if isinstance(messages[i], HumanMessage):
            new_messages[i] = HumanMessage(content=response.content)
            break


    return {
        "messages": new_messages,
        "was_rewritten": True,
        "rewrite_attempts": state.get("rewrite_attempts", 0) + 1,
    }


def generate_answer(state: MessagesState, response_model):
    """Generate an answer based on cleaned context and question."""
    question = _get_latest_user_question(state["messages"])
    logger.debug("Question: %s", question)
    raw_context = _get_latest_context(state["messages"])
    logger.debug(f"Raw context: {raw_context}")
    context = _clean_context(raw_context)
    logger.debug(f"context: {context}")

    prompt = GENERATE_PROMPT.format(question=question, context=context)
    response = response_model.invoke(prompt)

    return {"messages": [response]}
