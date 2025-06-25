# Biometric RAG Agent

A Retrieval-Augmented Generation (RAG) system for question answering and document search over Suprema Biostar2 documentation and related biometric security resources.

## Features
- **Document Parsing & Cleaning:**
  - Automated PDF parsing and cleaning using LlamaParse.
  - Cleaned data stored in `cleaned_data/` for efficient downstream processing.
- **Vector Database:**
  - Embedding generation with HuggingFace models (configurable).
  - Vector storage and retrieval using ChromaDB.
- **RAG Pipeline:**
  - Modular pipeline for document retrieval, question answering, and answer grading.
  - Supports both local and cloud LLMs (e.g., Gemini, Llama, OpenAI, HuggingFace).
- **API & Frontend:**
  - FastAPI backend with `/query` endpoint for chat and search.
  - Streamlit-based frontend for interactive chatbot experience.
- **Evaluation:**
  - Integrated evaluation scripts and metrics for LLM output quality.
- **Logging & Observability:**
  - Langfuse integration for tracing and monitoring.

## Project Structure
```
biometric-rag-agent/
├── cleaned_data/         # Cleaned text files from documentation
├── chroma_vector_db/     # Chroma vector database files
├── data/                 # Raw data (PDFs, etc.)
├── diagrams/             # System diagrams and images
├── evaluation/           # Evaluation scripts and metrics
├── frontend/             # Streamlit app and UI components
├── notebooks/            # Jupyter notebooks for prototyping
├── src/                  # Main source code (API, agent, data, vector_db, utils)
├── requirements.txt      # Python dependencies
├── Makefile              # Common commands
├── README.md             # Project documentation
└── ...
```

## Setup
1. **Install dependencies:**
   ```bash
   uv pip install -r requirements.txt
   # or, for full project management:
   uv pip install -r pyproject.toml
   ```
2. **Set environment variables:**
   - Copy `.env.example` to `.env` and fill in required API keys (Google, Langfuse, etc).
3. **Prepare data:**
   - Place raw PDFs in the `data/` directory.
   - Run the data cleaner:
     ```bash
     python -m src.data_cleaner
     ```
4. **Build vector indexes:**
   ```bash
   python -m src.index_builder
   ```
5. **Start the API server:**
   ```bash
   python -m src.main
   ```
6. **Run the frontend:**
   ```bash
   streamlit run frontend/app.py
   ```

## Running the App
You can use the provided `Makefile` to run the full application pipeline. The recommended steps are:

1. **Clean the data:**
   ```bash
   make clean-data
   ```
2. **Build vector indexes:**
   ```bash
   make index
   ```
3. **Run the backend API server:**
   ```bash
   make backend
   ```
4. **Run the frontend:**
   ```bash
   make frontend
   ```

You can also chain these commands as needed for your workflow.

## Usage
- Access the chatbot UI via the Streamlit app.
- Use the `/query` endpoint for programmatic access.
- Evaluate model performance using scripts in the `evaluation/` directory.

## Environment Variables
- `GOOGLE_API_KEY` - Google Gemini API key
- `DB_URL` - Database connection string
- `LANGFUSE_PUBLIC_KEY`, `LANGFUSE_SECRET_KEY`, `LANGFUSE_HOST_URL` - Langfuse observability
- See `.env.example` for all options

## Contributing
Pull requests and issues are welcome! Please ensure code is well-documented and tested.

## License
This project includes code and documentation under various open-source licenses. See the `cleaned_data/` directory for license details from upstream documentation sources.

---
For more information, see the system diagrams in `diagrams/` and notebooks in `notebooks/`.
