from langgraph.graph import MessagesState
from pydantic import BaseModel, Field
from typing import Literal
from langchain.output_parsers import BooleanOutputParser
from langchain.output_parsers.retry import RetryWithErrorOutputParser
from langchain_core.output_parsers import BaseOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

from src.agent.prompts import (
    GRADE_PROMPT,
    REWRITE_PROMPT,
    GENERATE_PROMPT,
    RELAVANCE_PROMPT,
    UNRELATED_QUERY_PROMPT,
)
from src.utils.logger import get_logger

logger = get_logger(__name__)


class GradeDocuments(BaseModel):
    """Grade documents using a binary score for relevance check."""

    binary_score: str = Field(
        description="Relevance score: 'yes' if relevant, or 'no' if not relevant"
    )


class RelevanceOutputParser(BaseOutputParser):
    """Parses output from the Relevance Classification LLM step."""

    def parse(self, text: str) -> str:
        cleaned = text.strip().upper()
        if cleaned in {"RELATED", "UNRELATED"}:
            return cleaned
        raise ValueError(
            f"Invalid relevance output: '{text}' (expected 'RELATED' or 'UNRELATED')"
        )

    @property
    def _type(self) -> str:
        return "relevance_output_parser"


def _clean_context(raw_text: str) -> str:
    """Clean up duplicated lines and excessive whitespace from retrieved context."""
    lines = raw_text.splitlines()
    unique_lines = list(dict.fromkeys(line.strip() for line in lines if line.strip()))
    return "\n".join(unique_lines)


def _get_latest_user_question(messages):
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            return msg.content
    raise ValueError("No user message found in the state.")


def _get_latest_context(messages):
    """Get the most recent context from ToolMessage (retrieval results)."""
    for msg in reversed(messages):
        if isinstance(msg, ToolMessage) and hasattr(msg, "content") and msg.content:
            return msg.content
    return ""


def query_relavance_checker(
    state: MessagesState, response_model    
) -> Literal["related", "unrelated"]:
    question = _get_latest_user_question(state["messages"])

    if not question:
        raise ValueError("Question is empty please try again")

    prompt_template = PromptTemplate.from_template(RELAVANCE_PROMPT)
    parser = RelevanceOutputParser()
    retrying_parser = RetryWithErrorOutputParser.from_llm(
        llm=response_model,
        parser=parser,
        prompt=prompt_template,
        max_retries=1,
    )

    input_values = {"question": question}
    prompt_value = prompt_template.format_prompt(**input_values)
    raw_output = response_model.invoke(prompt_value)

    try:
        result = retrying_parser.parse_with_prompt(
            completion=raw_output.content,
            prompt_value=prompt_value,
        )
        result = result.lower()
        logger.debug(f"Relavance result: {result}")
    except Exception as e:
        logger.error(f"Parser failed: {e}")
        return "unrelated"

    return result


def grade_documents(
    state: MessagesState, grader_model
) -> Literal["generate_answer", "rewrite_question"]:
    """Determine whether the retrieved documents are relevant to the question."""

    rewrite_attempts = state.get("rewrite_attempts", 0)
    logger.debug(f"Rewrite attempts: {rewrite_attempts}")

    # Check rewrite attempts limit first
    if rewrite_attempts >= 2:
        logger.warning("Rewrite attempts exceeded limit of 2")
        return "generate_answer"

    question = _get_latest_user_question(state["messages"])
    context = _get_latest_context(state["messages"])

    if not context:
        logger.warning("No context retrieved — skipping to rewrite.")
        return "rewrite_question"

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
        logger.debug(f"Grading result: {result}")
    except Exception as e:
        logger.error(f"Parser failed: {e}")
        return "rewrite_question"

    return "generate_answer" if result else "rewrite_question"


def check_query_relevance(state: MessagesState, response_model):
    """
    Check if the query is related to the knowledge base.
    Sets `relevance_result` in state: 'related' or 'unrelated'.
    """
    result = query_relavance_checker(state, response_model)
    return {
        "messages": state["messages"],
        "rewrite_attempts": state.get("rewrite_attempts", 0),
        "relevance_result": result,
    }


def unrelated_query_response(state: MessagesState, response_model):
    """
    Return a general response for unrelated/small talk queries.
    """
    question = _get_latest_user_question(state["messages"])
    prompt_template = PromptTemplate.from_template(UNRELATED_QUERY_PROMPT)

    input_values = {"question": question}
    prompt_value = prompt_template.format_prompt(**input_values)

    response = response_model.invoke(prompt_value)

    return {
        "messages": [response],
        "rewrite_attempts": state.get("rewrite_attempts", 0),
    }


def generate_query_or_respond(state: MessagesState, response_model, retriever_tool):
    response = response_model.bind_tools(tools=[retriever_tool]).invoke(
        state["messages"], tool_choice="auto"
    )

    return {
        "messages": [response],
        "rewrite_attempts": state.get("rewrite_attempts", 0),
    }


def rewrite_question(state: MessagesState, response_model):
    """Rewrite the latest user question and properly update state."""
    messages = state["messages"]
    question = _get_latest_user_question(messages)
    prompt = REWRITE_PROMPT.format(question=question)

    response = response_model.invoke([HumanMessage(content=prompt)])
    logger.debug(f"Rewrite response: {response}")

    if not hasattr(response, "content"):
        raise ValueError("Response from model is missing 'content' attribute")

    # Find and replace the most recent HumanMessage (the original question)
    new_messages = messages.copy()
    for i in reversed(range(len(new_messages))):
        if isinstance(new_messages[i], HumanMessage):
            new_messages[i] = HumanMessage(content=response.content)
            logger.debug(f"Replaced user question with: {response.content}")
            break
    else:
        raise ValueError("No HumanMessage found to rewrite")

    # Properly increment rewrite attempts
    current_attempts = state.get("rewrite_attempts", 0)
    new_attempts = current_attempts + 1

    logger.debug(
        f"Incrementing rewrite attempts from {current_attempts} to {new_attempts}"
    )

    return {
        "messages": new_messages,
        "rewrite_attempts": new_attempts,
    }


def generate_answer(state: MessagesState, response_model):
    """Generate an answer based on cleaned context and question."""
    question = _get_latest_user_question(state["messages"])
    logger.debug("Question: %s", question)
    raw_context = _get_latest_context(state["messages"])

    if not raw_context:
        logger.warning("No context found for answering. Skipping.")
        return {
            "messages": [
                AIMessage(
                    content="I couldn't find relevant information. Please try again."
                )
            ]
        }

    logger.debug(f"Raw context: {raw_context}")
    context = _clean_context(raw_context)
    logger.debug(f"Cleaned context: {context}")

    prompt = GENERATE_PROMPT.format(question=question, context=context)
    response = response_model.invoke(prompt)

    return {"messages": [response]}
