# Enterprise IT Support Agentic RAG Copilot

A practical internal IT support assistant built as a small LangGraph + FastAPI application. The app routes user questions, retrieves evidence from a private company knowledge base, grades it, falls back to external web search when needed, and returns grounded answers with a trace of the decision path.

This repository is a working demo of an enterprise-style agentic RAG workflow for internal knowledge support, not just a notebook experiment. It includes a web UI, REST API, Pinecone vector search, Google Gemini LLM orchestration, Tavily fallback search, and upload-based document ingestion.

## What this project does

The app is designed around a fictional company, NovaRetail, with an internal IT knowledge base. It answers questions such as:

- How do I connect to the company VPN?
- What is the password reset policy?
- What is the MFA requirement for remote access?
- How do I troubleshoot a slow laptop or email issue?
- When the internal KB is weak or missing, use web evidence and clearly label it as external information

It avoids answering from raw general knowledge when the private KB has enough evidence, and it explicitly distinguishes between:

- Company private KB answers
- Direct conversational replies
- External web answers
- Insufficient evidence states

## Problem being solved

Internal IT teams often have a large set of documents spread across:

- VPN instructions
- password and MFA policies
- laptop troubleshooting runbooks
- software installation standards
- service desk procedures
- compliance/security guidance

Employees still end up submitting repetitive tickets because:

- they do not know which document is authoritative
- keyword search returns noisy results
- generic chatbots can hallucinate
- internal knowledge can be stale or incomplete
- some questions require current vendor or public information

This project solves that by creating an agent that decides whether to answer from private knowledge, external search, or a simple conversational path.

## High-level architecture

```text
User / Employee
      |
      v
Web UI (HTML + JS)
      |
      v
FastAPI backend
      |
      v
LangGraph workflow
  - route question
  - retrieve private KB
  - grade evidence
  - optionally search web
  - rewrite and retry if needed
  - generate grounded answer
      |
      +-------------------------+
      |                         |
      v                         v
Private company KB          External web search
(Pinecone + embeddings)     (Tavily)
      |                         |
      +-----------+-------------+
                  |
                  v
          Gemini LLM
          (routing, grading, generation)
```

## Core features

- Private knowledge retrieval from Pinecone using embeddings
- Question routing between internal KB and direct chat
- Evidence grading before generating answers
- Fallback to Tavily web search when private KB evidence is weak
- Query rewrite and retry flow for better retrieval
- Source-aware response generation
- Trace logging for each stage of the LangGraph workflow
- SQLite-based audit table for recorded queries
- Upload API for indexing PDF/TXT/MD/DOCX files into Pinecone
- Browser UI for chat and document ingestion

## Project structure

```text
Agentic_AI_Copilot/
├── app/
│   ├── api/
│   │   └── routes.py              # /api/chat, /api/health, /api/ingest
│   ├── core/
│   │   ├── config.py              # environment settings and defaults
│   │   └── logging.py             # logging configuration
│   ├── rag/
│   │   ├── state.py               # typed state and structured LLM outputs
│   │   ├── vectorstore.py         # Pinecone + embeddings setup and retrieval
│   │   └── workflow.py            # LangGraph agent graph
│   ├── services/
│   │   ├── audit.py               # SQLite audit logging
│   │   └── ingestion.py           # file loading and chunking
│   └── main.py                    # FastAPI app bootstrap
├── data/
│   ├── audit.db                   # SQLite DB created at runtime
│   └── sample_kb/
│       ├── company_it_handbook.md
│       └── service_desk_runbook.md
├── static/
│   ├── css/
│   └── js/
│       └── app.js                 # frontend chat + upload logic
├── templates/
│   └── index.html                 # web UI for the assistant
├── uploads/                       # uploaded documents land here
├── .env.example                   # example environment config
├── .gitignore
├── ingest_sample_kb.py            # sample KB ingestion script
├── LICENSE
├── requirements.txt
├── run.py                         # app entry point
├── README.md
└── tests/
```

## Tech stack

- Python 3.11+
- FastAPI
- LangGraph
- LangChain Core + LangChain Community
- Google Gemini (`langchain-google-genai`)
- Pinecone vector database
- Tavily search API
- pypdf / python-docx / TextLoader for ingestion
- Jinja2 + HTML/CSS/JavaScript for frontend
- SQLite for audit logging

## Workflow logic

The actual LangGraph workflow is implemented in `app/rag/workflow.py`.

The flow is:

1. Route the question
   - If it is a greeting or casual chat, return a direct answer.
   - If it is an IT support question, continue to retrieval.

2. Retrieve from private KB
   - Use Pinecone vector search with the current query.

3. Grade private evidence
   - Ask the LLM to decide whether the retrieved company evidence is sufficient.
   - If good: generate an answer from the KB.
   - If weak: continue to web search.

4. Search the web with Tavily
   - Use the same question or rewritten query.

5. Grade web evidence
   - If good: generate a web-based answer.
   - If weak: optionally rewrite the query and retry private retrieval.

6. Generate answer with transparency
   - Apply source labeling such as `private_kb`, `web_search`, or `direct`.
   - Keep trace items for debugging and auditability.

## API endpoints

The FastAPI API is defined in `app/api/routes.py`.

### GET /api/health

Returns service health information.

Example response:

```json
{
  "status": "ok",
  "service": "Enterprise IT Support Agentic RAG Copilot"
}
```

### POST /api/chat

Sends a question to the agent and returns the answer plus runtime trace.

Request body:

```json
{
  "question": "How do I connect to the company VPN from home?"
}
```

Response shape:

```json
{
  "answer": "...",
  "source_used": "private_kb",
  "trace": ["Router → KB", "Private KB retrieval → 4 chunks"],
  "citations": [
    {
      "title": "company_it_handbook.md",
      "url": "",
      "type": "private_kb"
    }
  ],
  "rewritten_query": "..."
}
```

### POST /api/ingest

Uploads a file and indexes it into Pinecone.

- Supported files: `.pdf`, `.txt`, `.md`, `.docx`
- Requires `X-Admin-Key` header to match `ADMIN_API_KEY`
- Saves the file under `uploads/`
- Loads, chunks, embeds, and stores it in the configured Pinecone namespace

Example:

```bash
curl -X POST http://127.0.0.1:8080/api/ingest \
  -H "X-Admin-Key: change-me" \
  -F "file=@/path/to/company_policy.pdf"
```

## Environment variables

The project loads settings from a root `.env` file using `pydantic-settings`.

Example configuration is in `.env.example`.

```env
GEMINI_API_KEY=
GEMINI_MODEL=gemini-3.8-flash
EMBEDDING_MODEL=gemini-embedding-001

PINECONE_API_KEY=
PINECONE_INDEX_NAME=fde-it-support-rag
PINECONE_NAMESPACE=company-it-kb

TAVILY_API_KEY=
```

### Variable reference

- `GEMINI_API_KEY`: API key for Gemini LLM and embeddings
- `GEMINI_MODEL`: model used for routing, grading, and answer generation
- `EMBEDDING_MODEL`: embedding model to match Pinecone index dimension
- `PINECONE_API_KEY`: Pinecone API key
- `PINECONE_INDEX_NAME`: vector index name
- `PINECONE_NAMESPACE`: namespace for document isolation
- `TAVILY_API_KEY`: Tavily API key for external search fallback
- `ADMIN_API_KEY`: header secret for document ingestion endpoint
- `APP_ENV`: env label, default `development`

## Setup and running

### 1. Clone the repository

```bash
git clone https://github.com/kshitijprakash1717-jpg/Agentic_AI_Copilot.git
cd Agentic_AI_Copilot
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

On macOS/Linux:

```bash
source venv/bin/activate
```

On Windows:

```bash
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file at the project root:

```env
GEMINI_API_KEY=your_google_ai_key
GEMINI_MODEL=gemini-3.8-flash
EMBEDDING_MODEL=gemini-embedding-001

PINECONE_API_KEY=your_pinecone_key
PINECONE_INDEX_NAME=fde-it-support-rag
PINECONE_NAMESPACE=company-it-kb

TAVILY_API_KEY=your_tavily_key
ADMIN_API_KEY=change-me
```

### 5. Ensure Pinecone is ready

The app auto-creates the Pinecone index if it does not exist, as long as the index dimension matches the selected Gemini embedding model.

Important: the configured embedding model must match the Pinecone index dimension. The code currently supports:

- `gemini-embedding-001` -> dimension 3072

If the index already exists with a different dimension, the app raises an error and asks you to create a new index or migrate the data.

### 6. Load sample KB data

The repository includes sample docs under `data/sample_kb/`.

```bash
python ingest_sample_kb.py
```

This script loads each document, splits it into chunks, embeds the chunks with Gemini embeddings, and stores them in Pinecone.

### 7. Run the app

```bash
python run.py
```

Then open:

- http://127.0.0.1:8080
- FastAPI docs: http://127.0.0.1:8080/docs

## Sample knowledge base

The included sample docs are:

- `data/sample_kb/company_it_handbook.md`
- `data/sample_kb/service_desk_runbook.md`

These are intentionally fictional, but they demonstrate how internal policies and troubleshooting guidance can be indexed and retrieved by the agent.

## UI behavior

The web frontend includes:

- a chat pane for asking IT questions
- a trace panel showing LangGraph decisions
- a source badge for final answer origin
- example prompts
- an upload modal for indexing additional company docs

## Audit and traceability

Each chat request writes a record to SQLite under `data/audit.db`.

The table `query_audit` stores:

- timestamp
- question
- source_used
- trace_json

This gives you a lightweight audit trail for debugging and review.

## Security and production notes

This repo is a demo/internal tool foundation. For production use, consider:

- rotating `ADMIN_API_KEY`
- limiting access to admin ingestion endpoints
- storing secrets in a real secret manager instead of `.env`
- using authenticated user roles for IT staff documents
- validating uploaded files before indexing
- adding a proper content policy and moderation layer
- monitoring rate limits and LLM token usage
- reviewing web-source guidance before using external data in high-risk decisions

## Known implementation notes

- The app uses Google Gemini rather than Groq.
- The vector store is Pinecone-based and expects a matching embedding dimension.
- The agent chooses between `private_kb`, `web_search`, `direct`, and `insufficient_evidence` as its final source.
- Web fallback is clearly marked as external information to avoid overconfident answers.

## Example questions to try

- How do I connect to the company VPN from home?
- What is our password reset policy?
- Is MFA mandatory for remote access?
- What should I do if my laptop is lost or stolen?
- What is the process for software installation approval?
- What is the latest Microsoft Teams outage guidance?

## License

This project is licensed under the MIT License. See `LICENSE` for details.

## Summary

This project demonstrates an agentic RAG system for enterprise internal support that is more than a simple chatbot. It routes, evaluates evidence, chooses retrieval strategies, falls back to the web only when needed, and presents grounded answers with a decision trace.

It is a good starting point for building a secure internal knowledge assistant for IT operations, support workflows, and knowledge retrieval in enterprise environments.
