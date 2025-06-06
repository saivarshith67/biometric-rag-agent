from langgraph.checkpoint.memory import MemorySaver

def get_memory() -> MemorySaver:
    return MemorySaver()