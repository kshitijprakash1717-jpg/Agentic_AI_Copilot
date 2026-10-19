# Agentic AI Copilot — Enterprise IT Support Copilot

An end-to-end Forward Deployed Engineer (FDE) project that turns a notebook-style Agentic RAG workflow into a deployable internal product. This repository demonstrates how to build a secure IT Support Copilot that searches trusted private knowledge first, evaluates evidence quality, rewrites weak queries, and uses web search only when necessary.

Key technologies: FastAPI, LangGraph, Groq (LLM), Pinecone (vector DB), HuggingFace embeddings, Tavily web search, SQLite audit log, Docker, and a simple HTML/CSS/JavaScript UI.

---

## What this does

This project implements an "Agentic RAG" (Retrieval-Augmented Generation) workflow where the system:

- Routes incoming user questions (greeting vs IT support question).
- Retrieves evidence from a private Pinecone vector store.
- Grades private evidence (GOOD / WEAK).
- If evidence is WEAK, optionally performs a controlled web search (Tavily) and grades that evidence.
- Rewrites queries and retries retrieval when necessary.
- Produces grounded answers from Groq, and logs the decision path for transparency and debugging.

Example problems solved:
- "How do I connect to the company VPN from home?" (answer from private KB only)
- "What is the latest Microsoft Teams outage guidance?" (use web search when private KB is insufficient)

---

## Features

- Stateful routing and conditional decisions with LangGraph
- Grounded generation using Groq LLM
- Private enterprise knowledge in Pinecone
- Local 384-dim embeddings with HuggingFace all-MiniLM-L6-v2
- Web fallback via Tavily when private evidence is insufficient
- Simple web UI (static HTML/CSS/JS) and REST API (FastAPI)
- Basic audit trails in SQLite
- Document ingestion utilities (PDF/TXT/MD/DOCX) and chunking
- Dockerfile for reproducible deployments

---

## Repository layout

FDE_Agentic_RAG_IT_Copilot/

- app/
  - api/routes.py — Chat, health, and ingestion endpoints
  - core/config.py — Environment configuration
  - core/logging.py — Logging configuration
  - rag/state.py — LangGraph state and decision definitions
  - rag/vectorstore.py — Pinecone + embeddings wrapper
  - rag/workflow.py — The Agentic RAG graph implementation
  - services/audit.py — SQLite audit functions
  - services/ingestion.py — Document ingestion and chunking
  - main.py — FastAPI application
- data/sample_kb/ — Example knowledge base documents
- static/ — Frontend files (css, js)
- templates/index.html — Web UI
- tests/test_ingestion.py — Basic ingestion unit tests
- ingest_sample_kb.py — Helper to load the sample KB into Pinecone
- .env.example — Example environment variables
- Dockerfile — Container image
- run.py — Convenience script to run the app

---

## Quickstart — Local development

1. Clone the repo

   git clone https://github.com/kshitijprakash1717-jpg/Agentic_AI_Copilot.git
   cd Agentic_AI_Copilot

2. Create a virtual environment and install dependencies

   python -m venv .venv
   source .venv/bin/activate   # on Windows: .venv\\Scripts\\activate
   pip install -r requirements.txt

3. Copy and configure environment variables

   cp .env.example .env
   # Edit .env and fill in secrets: PINECONE_API_KEY, PINECONE_ENV, TAVILY_API_KEY, GROQ_API_KEY (or model settings), and any other required values.

4. (Optional) Ingest the sample KB

   # This will create embeddings and push them to Pinecone (ensure Pinecone creds are set in .env)
   python ingest_sample_kb.py

5. Run the app

   # Using the convenience runner
   python run.py

   # Or run with Uvicorn
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

6. Open the web UI

   Visit http://localhost:8000/ in your browser.

---

## Running in Docker

Build the image:

   docker build -t agentic-it-copilot:latest .

Run (example):

   docker run --env-file .env -p 8000:8000 agentic-it-copilot:latest

Note: Ensure any external services (Pinecone, Tavily, Groq) are accessible from the container and that credentials are present in the .env file.

---

## Configuration and environment variables

Important variables are shown in `.env.example`. Typical values you must provide:

- PINECONE_API_KEY — Pinecone API key
- PINECONE_ENV — Pinecone environment/region
- PINECONE_INDEX_NAME — Name of the index used for private KB
- TAVILY_API_KEY — API key for Tavily web search (fallback)
- GROQ_API_KEY — Groq LLM API key (or model config details)
- EMBEDDING_MODEL — (optional) embedding model id if configurable

Keep secrets out of source control. Use your preferred secret manager in production.

---

## Testing

Run the unit tests with pytest:

   pytest -q

There is a basic test for ingestion in `tests/test_ingestion.py`.

---

## Operational notes

- Audit: Decisions, retrieved snippets, evidence grading, and generation steps are logged to a SQLite DB for traceability.
- Security: The system is designed to prefer private KB evidence. Web searches are used only when grading logic marks private evidence as insufficient.
- Extensibility: The LangGraph workflow allows adding more states/branches to support additional business rules.

---

## Contributing

Contributions are welcome. Suggested workflow:

- Fork the repo
- Create a feature branch
- Run tests and linting locally
- Open a pull request describing your changes

Please avoid adding secrets or large binary files to the repository.

---

## Troubleshooting

- Pinecone errors: verify API key, index name, and that embeddings were successfully pushed.
- LLM / Groq errors: check API key, model configuration, and rate limits.
- Missing or stale KB answers: re-run ingestion after updating documents.

If you need help, open an issue in the repository with logs and steps to reproduce.

---

## License

This repository does not include a license file by default. Add a LICENSE file (for example MIT) if you want to make the project open source.

---

## Author

Forward Deployed Engineer project by the repository owner.

