FROM python:3.11-slim

# Install system dependencies and clean up in same layer to reduce image size
RUN apt-get update && \
    apt-get install -y nginx curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip install uv

# Set working directory
WORKDIR /app

# Copy dependency files first for better layer caching
COPY pyproject.toml uv.lock ./

# Install Python dependencies
RUN uv sync

# Copy application code
COPY ./src /app/src
COPY ./cleaned_data /app/cleaned_data
COPY Makefile /app/

# activate the virtual environment
RUN source .venv/bin/activate
# Build index (make sure this step doesn't fail)
RUN python -m src.index_builder

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# Expose port
EXPOSE 8000

# Use exec form for better signal handling
CMD ["python", "-m", "src.main"]