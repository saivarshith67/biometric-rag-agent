# ================================
# STAGE 1: Builder - Install dependencies
# ================================
FROM python:3.11.13-slim as builder

# Install uv
RUN pip install --no-cache-dir uv

WORKDIR /app

# Copy only dependency files
COPY pyproject.toml ./

# Create venv and install dependencies
RUN uv venv /opt/venv && \
    uv sync --no-dev --venv /opt/venv

# ================================
# STAGE 2: Runtime
# ================================
FROM python:3.11.13-slim

# System certs and curl if needed
RUN apt-get update && \
    apt-get install -y --no-install-recommends ca-certificates && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy virtual environment
COPY --from=builder /opt/venv /opt/venv

# Set PATH to use venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Copy app code
COPY ./src /app/src
COPY ./chroma_vector_db /app/chroma_vector_db

# Create user and switch
RUN useradd --create-home appuser && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

CMD ["python", "-m", "src.main"]
