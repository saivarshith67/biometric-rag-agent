from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.postgres import PostgresSaver

def get_memory() -> MemorySaver:
    return MemorySaver()