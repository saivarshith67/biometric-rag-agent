from langgraph.graph import MessagesState
from pydantic import BaseModel, Field
from src.agent.prompts import GRADE_PROMPT, REWRITE_PROMPT, GENERATE_PROMPT
from typing import Literal
from langchain.output_parsers import BooleanOutputParser
from langchain.output_parsers.retry import RetryWithErrorOutputParser
from langchain_core.prompts import PromptTemplate

class GradeDocuments(BaseModel):
    """Grade documents using a binary score for relevance check."""

    binary_score: str = Field(
        description="Relevance score: 'yes' if relevant, or 'no' if not relevant"
    )



def generate_query_or_respond(state: MessagesState, response_model, retriever_tool):
    response = response_model.bind_tools(
        tools=[retriever_tool]
    ).invoke(state["messages"], tool_choice="auto")

    return {"messages" : [response]}

def grade_documents(
    state: MessagesState,
    grader_model  # e.g. ChatOpenAI or similar
) -> Literal["generate_answer", "rewrite_question"]:
    """Determine whether the retrieved documents are relevant to the question."""

    question = state["messages"][0].content
    context = state["messages"][-1].content

    # Prepare the prompt
    prompt_template = PromptTemplate.from_template(GRADE_PROMPT)

    # Create parser and retry wrapper
    parser = BooleanOutputParser()  # returns True or False
    retrying_parser = RetryWithErrorOutputParser.from_llm(
        llm=grader_model,
        parser=parser,
        prompt=prompt_template,
        max_retries=1,
    )

    # Prepare the input values for the prompt
    input_values = {"question": question, "context": context}
    prompt_value = prompt_template.format_prompt(**input_values)

    # Get raw output from LLM
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