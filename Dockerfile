FROM python-3.11.13:slim

WORKDIR /app

RUN pip install uv

COPY pyproject.toml /app/
COPY ./src /app/src
COPY ./chroma_vector_db /app/chroma_vector_db

RUN uv sync

RUN . .venv/bin/activate

EXPOSE 8000

CMD ["python", "-m", "src.main"]