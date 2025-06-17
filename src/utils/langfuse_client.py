# src/utils/langfuse_client.py

from functools import wraps
import uuid

from langfuse import Langfuse
from src.config import LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, LANGFUSE_HOST_URL

# Initialize the Langfuse client
langfuse = Langfuse(
    public_key=LANGFUSE_PUBLIC_KEY,
    secret_key=LANGFUSE_SECRET_KEY,
    host=LANGFUSE_HOST_URL,
)

def traced(name: str):
    """
    Decorator to wrap any function with Langfuse trace and auto-log input/output.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create a unique trace
            trace = langfuse.create_trace(
                id=str(uuid.uuid4()),
                name=name,
                input={
                    "args": str(args),
                    "kwargs": str(kwargs),
                },
            )

            # Start a span inside this trace
            span = trace.create_span(name=f"{name}-span")

            try:
                result = func(*args, **kwargs)
                span.end(output=result)
                trace.update(output=result, status="SUCCESS")
                return result
            except Exception as e:
                span.end(output={"error": str(e)}, status="ERROR")
                trace.update(status="ERROR", metadata={"exception": str(e)})
                raise

        return wrapper
    return decorator
