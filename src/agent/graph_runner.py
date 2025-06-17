from src.utils.logger import get_logger
from langchain_core.messages import BaseMessage, AIMessage, ToolMessage, HumanMessage

logger = get_logger(__name__)


def stream_graph_response(graph, query: str, thread_id: str):
    """
    Stream the response from the LangGraph graph given a query and thread_id.

    Args:
        graph: The compiled StateGraph instance.
        query (str): The user query string.
        thread_id (str): Identifier for the conversation thread.

    Returns:
        The final message content from the last node in the stream, or a fallback response.
    """
    input_payload = {
        "messages": [
            {
                "role": "user",
                "content": query,
            }
        ]
    }
    config = {"thread_id": thread_id}

    final_response = []

    for chunk in graph.stream(input=input_payload, config=config):
        for node, update in chunk.items():
            logger.debug(f"\n\n\nUpdate from node : {node}")
            latest_update = update.get("messages", [])
            if latest_update:
                logger.debug(f"{latest_update}\n\n\n")
                final_response = (
                    latest_update  # capture the most recent non-empty messages
                )

    logger.info(f"final_response={final_response}")

    # Handle empty or malformed response gracefully
    if not final_response:
        logger.warning("No response messages were returned by the graph.")
        return "I couldn't generate a response. Please try rephrasing your question."

    last_msg = final_response[-1]

    if isinstance(last_msg, (AIMessage, ToolMessage, HumanMessage)):
        return last_msg.content or "No content available in the final message."
    elif isinstance(last_msg, BaseMessage):
        # fallback for other LangChain message types
        return getattr(last_msg, "content", "Unknown message format.")
    else:
        logger.error("Unexpected message type in final_response.")
        return "Unexpected error occurred in processing your query."
