# ================================
# STAGE 1: Builder - Install deps & download model
# ================================
FROM python:3.11.13-slim AS builder

# Install pip, uv
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl ca-certificates && \
    pip install --no-cache-dir uv

WORKDIR /app

# Copy dependency definitions
COPY pyproject.toml uv.lock ./

# Install torch CPU version first to reduce size
RUN pip install --no-cache-dir torch==2.3.0+cpu --index-url https://download.pytorch.org/whl/cpu

# Create virtualenv and install only production deps
RUN uv venv /opt/venv && \
    uv sync --no-dev --venv /opt/venv

# Pre-download model (40MB) into cache
RUN /opt/venv/bin/python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# ================================
# STAGE 2: Runtime - Slim image
# ================================
FROM python:3.11.13-slim

# Add system certificates
RUN apt-get update && \
    apt-get install -y --no-install-recommends ca-certificates && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy cached model to avoid downloading at runtime
COPY --from=builder /root/.cache /root/.cache

WORKDIR /app

# Copy your app code and vector DB
COPY ./src /app/src
COPY ./chroma_vector_db /app/chroma_vector_db

# Optional cleanup: remove metadata to shrink image further
RUN rm -rf /root/.cache/pip \
           /opt/venv/lib/python3.11/site-packages/**/*.dist-info \
           /opt/venv/lib/python3.11/site-packages/**/*.egg-info

# Create unprivileged user
RUN useradd --create-home appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000
CMD ["python", "-m", "src.main"]
