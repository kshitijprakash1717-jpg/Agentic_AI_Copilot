# Enterprise IT Support Agentic RAG Copilot

A production-style internal IT support assistant built with FastAPI, LangGraph, Google Gemini, Pinecone, and Tavily.

This project demonstrates an agentic retrieval-augmented generation workflow for enterprise knowledge support: it routes questions, checks whether the private knowledge base is sufficient, falls back to external search when needed, and returns grounded answers with a visible decision trace.

## Why this project exists

Internal IT teams often have the answers they need scattered across:

- VPN setup guides
- password and MFA policies
- software approval rules
- laptop troubleshooting runbooks
- service desk procedures
- compliance and access documentation

Search alone is not enough because employees often ask questions that are either:

- covered by internal documentation but hard to find
- missing from internal docs and require current public information
- ambiguous enough that a generic chatbot may hallucinate

This app solves that by making the system decide how to answer, rather than blindly generating from a single source.

## What it does

- Routes IT questions versus casual conversation
- Uses a private knowledge base first
- Grades retrieved evidence before answering
- Falls back to Tavily web search when the internal KB is weak
- Rewrites and retries queries to improve retrieval quality
- Returns the answer along with a trace of the decision path
- Supports document ingestion for internal policy uploads
- Logs chat activity to SQLite for auditability

## Architecture

```text
User / Employee
      |
      v
Web UI (HTML + JS)
      |
      v
FastAPI API
      |
      v
LangGraph workflow
  - route question
  - retrieve private KB
  - grade evidence
  - search web if needed
  - rewrite and retry
  - generate grounded answer
      |
      +------------------------+
      |                        |
      v                        v
Private KB                External web
(Pinecone + embeddings)   (Tavily search)
      |                        |
      +-----------+------------+
                  |
                  v
          Google Gemini LLM
```

## Features

- Private retrieval over Pinecone using Gemini embeddings
- Structured question routing with LangGraph
- Evidence grading before generation
- Web fallback for current or vendor-specific information
- Answer source labeling: `private_kb`, `web_search`, `direct`, or `insufficient_evidence`
- Upload API for PDF, TXT, MD, and DOCX ingestion
- Browser-based chat interface and trace panel
- Audit logging via SQLite

## Tech stack

- Python
- FastAPI
- LangGraph
- LangChain Core / Community
- Google Gemini (`langchain-google-genai`)
- Pinecone vector database
- Tavily search API
- Jinja2 + HTML/CSS/JavaScript
- SQLite
- `pypdf`, `python-docx`, `langchain-text-splitters`

## Repository structure

```text
Agentic_AI_Copilot/
├── app/
│   ├── api/
│   │   └── routes.py              # chat, health, and ingest endpoints
│   ├── core/
│   │   ├── config.py              # settings and environment defaults
│   │   └── logging.py             # logging setup
│   ├── rag/
│   │   ├── state.py               # typed graph state and Pydantic models
│   │   ├── vectorstore.py         # Pinecone setup and vector retrieval
│   │   └── workflow.py            # LangGraph agent logic
│   ├── services/
│   │   ├── audit.py               # SQLite audit logging
│   │   └── ingestion.py           # file load + chunking logic
│   └── main.py                    # FastAPI app bootstrap
├── data/
│   ├── audit.db                   # local SQLite database (created runtime)
│   └── sample_kb/
│       ├── company_it_handbook.md
│       └── service_desk_runbook.md
├── static/
│   ├── css/
│   └── js/
│       └── app.js                 # frontend behavior
├── templates/
│   └── index.html                 # chat UI
├── uploads/                       # uploaded documents
├── .env.example                   # example environment settings
├── .gitignore
├── ingest_sample_kb.py            # sample KB ingestion script
├── LICENSE
├── requirements.txt
├── run.py                         # local dev server entry point
├── README.md
└── tests/
```

## Getting started

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

Create a `.env` file in the project root with the required values:

```env
GEMINI_API_KEY=your_google_gemini_key
GEMINI_MODEL=gemini-3.8-flash
EMBEDDING_MODEL=gemini-embedding-001

PINECONE_API_KEY=your_pinecone_key
PINECONE_INDEX_NAME=fde-it-support-rag
PINECONE_NAMESPACE=company-it-kb

TAVILY_API_KEY=your_tavily_key
ADMIN_API_KEY=change-me
```

Example file is also provided in `.env.example`.

## Required environment variables

| Variable | Purpose | Required |
| --- | --- | --- |
| `GEMINI_API_KEY` | API key for Gemini LLM and embeddings | Yes |
| `GEMINI_MODEL` | LLM used by the routing, grading, and answer-generation flow | No (default: `gemini-3.8-flash`) |
| `EMBEDDING_MODEL` | Embedding model for Pinecone indexing and retrieval | No (default: `gemini-embedding-001`) |
| `PINECONE_API_KEY` | Pinecone API key | Yes |
| `PINECONE_INDEX_NAME` | Pinecone index name | No |
| `PINECONE_NAMESPACE` | Namespace used to isolate knowledge documents | No |
| `TAVILY_API_KEY` | API key for web fallback search | Yes |
| `ADMIN_API_KEY` | Secret for the upload/indexing endpoint | No |

## Important notes

- The app expects a Pinecone index whose dimension matches the configured embedding model.
- The current embedding configuration is compatible with `gemini-embedding-001`, which uses a dimension of 3072.
- If the index already exists with a different dimension, the app will raise a configuration error and ask you to create a new index or migrate your data.
- In production, rotate `ADMIN_API_KEY` and avoid committing secrets to git.

## Load the sample knowledge base

The project includes demo IT documents under `data/sample_kb/`.

```bash
python ingest_sample_kb.py
```

This script:

1. loads all sample files
2. splits them into chunks
3. embeds the chunks with Gemini embeddings
4. stores them in Pinecone

## Run the application

```bash
python run.py
```

Open the app in your browser:

- http://127.0.0.1:8080
- API docs: http://127.0.0.1:8080/docs

## API

### Health check

```bash
curl http://127.0.0.1:8080/api/health
```

Response:

```json
{
  "status": "ok",
  "service": "Enterprise IT Support Agentic RAG Copilot"
}
```

### Chat

```bash
curl -X POST http://127.0.0.1:8080/api/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "How do I connect to the company VPN from home?"}'
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

### Ingest document

Upload a file and index it into Pinecone:

```bash
curl -X POST http://127.0.0.1:8080/api/ingest \
  -H "X-Admin-Key: change-me" \
  -F "file=@/path/to/company_policy.pdf"
```

Supported extensions:

- `.pdf`
- `.txt`
- `.md`
- `.docx`

## How the agent works

The workflow in `app/rag/workflow.py` follows this pattern:

1. Route the user question
   - greetings and casual chat go to a direct response
   - IT support questions continue to retrieval
2. Retrieve from the private KB
3. Grade the evidence
4. If it is weak, search the web with Tavily
5. Grade the web evidence
6. Rewrite the query and retry if needed
7. Generate a grounded answer and attach a trace

This makes the application more reliable than a basic RAG pipeline because it can decide when to answer from internal docs, when to search the web, and when to refuse to answer due to insufficient evidence.

## Sample use cases

- "How do I connect to the company VPN from home?"
- "What is our password reset policy?"
- "Is MFA mandatory for remote access?"
- "What should I do if my laptop is lost or stolen?"
- "What is the process for software installation approval?"
- "What is the latest Microsoft Teams outage guidance?"

## Audit trail

Each chat request is recorded in SQLite under `data/audit.db`.

The `query_audit` table stores:

- timestamp
- question
- selected source
- trace JSON

This is useful for debugging, observability, and internal review.

## Security considerations

This is a demo and internal-tool foundation. For real deployment, consider:

- rotating `ADMIN_API_KEY`
- securing the upload endpoint behind auth and access control
- storing secrets in a secret manager instead of `.env`
- validating uploaded files before indexing
- restricting access to internal docs and policies
- adding role-based access and stronger audit controls

## License

This project is licensed under the MIT License. See `LICENSE` for more details.

## Summary

This repository is a practical example of an enterprise-grade agentic RAG system for IT support. It moves beyond a simple chatbot by combining:

- internal document retrieval
- external search fallback
- evidence grading
- query rewriting
- traceability
- API + UI deployment

It is designed to show how an internal support copilot can be built as a real product, not just as a notebook prototype.
