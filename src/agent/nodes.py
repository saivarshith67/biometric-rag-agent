# src.agent.nodes


from src.agent.prompts import (
    GRADE_PROMPT,
    REWRITE_PROMPT,
    GENERATE_PROMPT,
    RELAVANCE_PROMPT,
    UNRELATED_QUERY_PROMPT,
)
from src.utils.logger import get_logger
from langfuse import observe
from langfuse.langchain import CallbackHandler
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import BaseOutputParser
from langchain.output_parsers.retry import RetryWithErrorOutputParser
from langchain.output_parsers import BooleanOutputParser
from pydantic import BaseModel, Field
from typing import Literal, cast
from src.agent.state import State


logger = get_logger(__name__)
langfuse_handler = CallbackHandler()


class GradeDocuments(BaseModel):
    binary_score: str = Field(
        description="Relevance score: 'yes' if relevant, or 'no' if not relevant"
    )


class RelevanceOutputParser(BaseOutputParser):
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
    lines = raw_text.splitlines()
    unique_lines = list(dict.fromkeys(line.strip() for line in lines if line.strip()))
    return "\n".join(unique_lines)


def _get_latest_user_question(messages):
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            return msg.content
    raise ValueError("No user message found in the state.")


def _get_latest_context(messages):
    for msg in reversed(messages):
        if isinstance(msg, ToolMessage) and hasattr(msg, "content") and msg.content:
            return msg.content
    return ""


@observe()
def initialize_current_query(state: State) -> State:
    for msg in reversed(state["messages"]):
        if isinstance(msg, HumanMessage):
            new_state = state.copy()
            new_state["current_query"] = msg.content
            new_state["was_rewritten"] = False
            new_state["rewrite_attempts"] = 0
            return new_state

    raise ValueError("No user message found to initialize current_query")


@observe(name="query_relevance_checker", as_type="generation")
def query_relavance_checker(state: State, response_model) -> State:
    question = state.get("current_query")

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


    raw_output = response_model.invoke(
        prompt_value, config={"callbacks": [langfuse_handler]}
    )

    try:
        result = retrying_parser.parse_with_prompt(
            completion=raw_output.content,
            prompt_value=prompt_value,
        ).lower()
        logger.debug(f"Relevance result: {result}")
    except Exception as e:
        logger.error(f"Parser failed: {e}")
        result = "unrelated"

    return result


@observe()
def grade_documents(
    state: State, grader_model
) -> Literal["generate_answer", "rewrite_question"]:
    if state["rewrite_attempts"] >= 2:
        logger.warning("Rewrite attempts exceeded limit of 2")
        return "generate_answer"

    question = state["current_query"]
    context = state["messages"][-1]

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
    raw_output = grader_model.invoke(prompt_value, config={"callbacks": [langfuse_handler]})

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


@observe()
def check_query_relevance(state: State, response_model) -> State:
    question = state.get("current_query")
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
    raw_output = response_model.invoke(prompt_value, config={"callbacks": [langfuse_handler]})

    try:
        result = retrying_parser.parse_with_prompt(
            completion=raw_output.content,
            prompt_value=prompt_value,
        ).lower()
        logger.debug(f"Relevance result: {result}")
    except Exception as e:
        logger.error(f"Parser failed: {e}")
        result = "unrelated"

    return {
        **state,
        "relevance": result,
    }


@observe()
def unrelated_query_response(state: State, response_model) -> State:
    question = state["current_query"]
    prompt_template = PromptTemplate.from_template(UNRELATED_QUERY_PROMPT)

    input_values = {"question": question}
    prompt_value = prompt_template.format_prompt(**input_values)
    response = response_model.invoke(prompt_value, config={"callbacks": [langfuse_handler]})

    return {
        **state,
        "messages": state["messages"] + [AIMessage(content=response.content)],
    }


@observe()
def generate_retriever_tool_call(state: State, response_model, retriever_tool) -> State:
    response = response_model.bind_tools(tools=[retriever_tool]).invoke(
        state["current_query"], tool_choice="auto", config={"callbacks": [langfuse_handler]}
    )

    return {
        **state,
        "messages": state["messages"] + [response],
    }


@observe()
def rewrite_question(state: State, response_model) -> State:
    question = state["current_query"]
    logger.info(f"Current query : {question}")
    prompt = REWRITE_PROMPT.format(question=question)

    response = response_model.invoke([HumanMessage(content=prompt)], config={"callbacks": [langfuse_handler]})
    logger.debug(f"Rewrite response: {response}")


    return {
        **state,
        "messages": state["messages"] + [response],
        "current_query": response.content,
        "rewrite_attempts": state["rewrite_attempts"] + 1,
        "was_rewritten": True,
    }

@observe()
def generate_answer(state: State, response_model) -> State:
    question = state["current_query"]

    # Step 1: Find index of the last HumanMessage (i.e., the current query)
    last_human_index = -1
    for i in reversed(range(len(state["messages"]))):
        if isinstance(state["messages"][i], HumanMessage):
            last_human_index = i
            break

    if last_human_index == -1:
        raise ValueError("No HumanMessage found for the current query.")

    # Step 2: Collect ToolMessages that are responses to this query (i.e., after HumanMessage)
    tool_messages = [
        msg for msg in state["messages"][last_human_index + 1 :]
        if isinstance(msg, ToolMessage) and getattr(msg, "content", None)
    ]

    if not tool_messages:
        return {
            **state,
            "messages": state["messages"]
            + [AIMessage(content="I couldn't find relevant information. Please try again.")]
        }

    # Step 3: Concatenate and clean context
    combined_context = "\n".join(_clean_context(msg.content) for msg in tool_messages)

    logger.info("INSIDE GENERATE ANSWER")
    logger.info(f"CLEANED CONTEXT = {combined_context}")

    # Step 4: Format prompt and generate answer
    prompt = GENERATE_PROMPT.format(question=question, context=combined_context)
    response = response_model.invoke(prompt, config={"callbacks": [langfuse_handler]})

    return {
        **state,
        "messages": state["messages"] + [AIMessage(content=response.content)],
    }


@observe()
def generate_web_search_tool_call(state: State, response_model, search_tool) -> State:
    response = response_model.bind_tools(tools=[search_tool]).invoke(
        state["messages"], tool_choice="auto", config={"callbacks": [langfuse_handler]}
    )

    return {
        **state,
        "messages": state["messages"] + [response],
    }
