def stream_graph_response(graph, query: str, thread_id: str):
    """
    Stream the response from the LangGraph graph given a query and thread_id.

    Args:
        graph: The compiled StateGraph instance.
        query (str): The user query string.
        thread_id (str): Identifier for the conversation thread.

    Returns:
        None (prints updates as they come)
    """
    input_payload = {
        "messages": [
            {
                "role": "user",
                "content": query,
            }
        ]
    }
    config = {
        "thread_id": thread_id
    }

    for chunk in graph.stream(input=input_payload, config=config):
        for node, update in chunk.items():
            print("Update from node", node)
            update["messages"][-1].pretty_print()
            print("\n\n")
