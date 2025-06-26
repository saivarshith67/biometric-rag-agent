FROM python:3.11-alpine

WORKDIR /app

# Install uv
RUN pip install uv

# Copy dependency files first for better caching
COPY pyproject.toml /app/

# Install dependencies
RUN uv sync

# Copy application code
COPY ./src /app/src
COPY ./chroma_vector_db /app/chroma_vector_db

# Expose port
EXPOSE 8000

# Run the application using uv
CMD ["uv", "run", "python", "-m", "src.main"]