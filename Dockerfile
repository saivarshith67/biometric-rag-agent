# Step-by-step debugging - uncomment one section at a time
FROM python:3.11-slim

# STEP 1: Check base image size
RUN echo "=== STEP 1: BASE IMAGE ===" && \
    df -h / && \
    echo "Root directory size:" && \
    du -sh / 2>/dev/null || echo "Cannot measure root"

# STEP 2: Install system packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends nginx curl && \
    rm -rf /var/lib/apt/lists/* && \
    echo "=== STEP 2: AFTER SYSTEM PACKAGES ===" && \
    df -h /

# STEP 3: Install uv
RUN pip install --no-cache-dir uv && \
    echo "=== STEP 3: AFTER UV INSTALL ===" && \
    df -h /

WORKDIR /app

# STEP 4: Copy dependency files and check their size
COPY pyproject.toml uv.lock ./
RUN echo "=== STEP 4: DEPENDENCY FILES ===" && \
    ls -lah pyproject.toml uv.lock && \
    echo "Lock file line count:" && \
    wc -l uv.lock && \
    echo "Sample dependencies from lock file:" && \
    head -50 uv.lock

# STEP 5: This is where the explosion likely happens
# Run uv sync and check size before/after
RUN echo "=== STEP 5: BEFORE UV SYNC ===" && \
    df -h / && \
    echo "Starting uv sync..." && \
    uv sync --no-dev --verbose && \
    echo "=== AFTER UV SYNC ===" && \
    df -h / && \
    echo ".venv directory size:" && \
    du -sh .venv && \
    echo "Top 10 largest items in .venv:" && \
    find .venv -type f -exec du -sh {} + 2>/dev/null | sort -hr | head -10

# STEP 6: Check what packages were actually installed
RUN echo "=== STEP 6: INSTALLED PACKAGES ANALYSIS ===" && \
    echo "Site-packages contents:" && \
    ls -la .venv/lib/python*/site-packages/ | head -20 && \
    echo "" && \
    echo "Largest packages by size:" && \
    du -sh .venv/lib/python*/site-packages/* 2>/dev/null | sort -hr | head -15 && \
    echo "" && \
    echo "Looking for known large packages:" && \
    find .venv -type d -name "*torch*" -o -name "*tensorflow*" -o -name "*transformers*" -o -name "*opencv*" -o -name "*scipy*" -o -name "*numpy*" 2>/dev/null

# STEP 7: Clean caches and check again
RUN uv cache clean && \
    rm -rf /root/.cache/* /tmp/* /var/tmp/* && \
    echo "=== STEP 7: AFTER CACHE CLEAN ===" && \
    df -h / && \
    du -sh .venv

# Uncomment these one by one to test:

# # STEP 8: Copy your source code
# COPY ./src /app/src
# RUN echo "=== STEP 8: AFTER COPYING SRC ===" && \
#     du -sh src && \
#     df -h /

# # STEP 9: Copy vector database
# COPY ./chroma_vector_db /app/chroma_vector_db  
# RUN echo "=== STEP 9: AFTER COPYING VECTOR DB ===" && \
#     du -sh chroma_vector_db && \
#     find chroma_vector_db -type f -size +10M 2>/dev/null && \
#     df -h /