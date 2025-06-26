FROM python:3.11-slim

# Do EVERYTHING in one RUN command to avoid layer bloat
RUN apt-get update && \
    apt-get install -y --no-install-recommends nginx curl && \
    pip install --no-cache-dir uv && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* /root/.cache/*

WORKDIR /app

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies and clean up in ONE layer
RUN uv sync --no-dev && \
    uv cache clean && \
    rm -rf /root/.cache/* /tmp/* /var/tmp/*

# Copy application code
COPY ./src /app/src
COPY ./chroma_vector_db /app/chroma_vector_db

# Create user and set permissions
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app

ENV PATH="/app/.venv/bin:$PATH"
USER app

EXPOSE 8000
CMD ["python", "-m", "src.main"]