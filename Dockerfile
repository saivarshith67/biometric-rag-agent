# ================================
# STAGE 1: Builder - Install dependencies
# ================================
FROM python:3.11-slim as builder

# Install uv and any build dependencies needed
RUN pip install --no-cache-dir uv

WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

RUN uv lock

# Install Python dependencies (this creates the bloated cache)
RUN uv sync --no-dev

# ================================
# STAGE 2: Production - Clean runtime image
# ================================
FROM python:3.11-slim

# Install only runtime system dependencies in one layer
RUN apt-get update && \
    apt-get install -y --no-install-recommends nginx curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

WORKDIR /app

# Copy ONLY the virtual environment from builder (no cache, no bloat)
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY ./src /app/src
COPY ./chroma_vector_db /app/chroma_vector_db

# Create user and set permissions
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app

# Set PATH to use the virtual environment
ENV PATH="/app/.venv/bin:$PATH"

# Switch to non-root user
USER app

# Expose port
EXPOSE 8000

# Use exec form for better signal handling
CMD ["python", "-m", "src.main"]