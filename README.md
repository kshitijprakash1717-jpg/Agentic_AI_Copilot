# Agentic_AI_Copilot

Enterprise IT Support Agentic RAG Copilot
An end-to-end Forward Deployed Engineer (FDE) project that turns a notebook-style Agentic RAG workflow into a deployable internal product using LangGraph, FastAPI, Pinecone, Groq, Tavily, HTML, CSS, and JavaScript.

1. Business Problem
   Customer
   NovaRetail, a fictional 3,000-employee retail company.

Problem
The internal IT team maintains many documents: VPN instructions, password rules, MFA policy, software installation rules, laptop troubleshooting guides, and service-desk runbooks.

Employees still create repetitive support tickets because:

They do not know where the correct document is.
Traditional keyword search returns too many results.
A normal chatbot may hallucinate an answer.
Internal documents can be incomplete or outdated.
Some questions require current vendor information from the public web.
Example
An employee asks:

“How do I connect to the company VPN from home?”

The answer exists in the private company KB, so the system should not search the public internet.

Another employee asks:

“What is the latest Microsoft Teams outage guidance?”

The internal KB may not contain current outage information. The system should recognize weak private evidence, use an external search, grade that evidence, and answer with an external-source warning.

Business Goal
Build a secure IT Support Copilot that:

Searches trusted private knowledge first.
Checks whether retrieved evidence is good enough.
Uses web search only when private knowledge is insufficient.
Rewrites weak queries and retries.
Generates grounded answers.
Shows the decision path for transparency and debugging.
Lets authorized staff add new company documents. 2. Why This Is an FDE Project
A Forward Deployed Engineer does more than create an LLM notebook. The FDE must turn the customer's problem into a usable product.

Customer Problem
↓
Discovery & Requirements
↓
Solution Architecture
↓
Data / Knowledge Integration
↓
Agentic RAG Development
↓
API Development
↓
User Interface
↓
Security + Audit + Testing
↓
Deployment
↓
Observe + Improve
This repository demonstrates each layer.

3. Simple Architecture
   ┌─────────────────────┐
   │ Employee / User │
   └──────────┬──────────┘
   │
   ▼
   ┌─────────────────────┐
   │ HTML/CSS/JavaScript │
   │ Web UI │
   └──────────┬──────────┘
   │ POST /api/chat
   ▼
   ┌─────────────────────┐
   │ FastAPI │
   └──────────┬──────────┘
   │
   ▼
   ┌─────────────────────┐
   │ LangGraph │
   │ Agentic RAG Control │
   └──────────┬──────────┘
   │
   ┌──────────────┴──────────────┐
   │ │
   ▼ ▼
   ┌───────────────┐ ┌──────────────┐
   │ Private KB │ │ Tavily Web │
   │ Pinecone │ │ Search │
   └───────┬───────┘ └──────┬───────┘
   │ │
   └──────────────┬──────────────┘
   ▼
   ┌────────────────┐
   │ Groq LLM │
   │ Grounded Answer│
   └────────────────┘
4. Agentic RAG Workflow
   This follows the same core implementation pattern as the reference notebook.

Question
↓
[1] Route Question
├── Greeting / simple chat ─────────────→ Direct Answer
│
└── IT support question
↓
[2] Retrieve from Private Pinecone KB
↓
[3] Grade Private Evidence
┌────────┴────────┐
│ │
GOOD WEAK
│ │
▼ ▼
Generate from KB [4] Tavily Web Search
↓
[5] Grade Web Evidence
┌────┴─────┐
│ │
GOOD WEAK
│ │
▼ ▼
Generate Web [6] Rewrite Query
↓
Retry Private KB
↓
Max retry reached?
↓
Insufficient Evidence
Why Agentic?
Normal RAG does approximately this:

Question → Retrieve → Generate
This project makes decisions:

Question
→ Route
→ Retrieve
→ Evaluate evidence
→ Choose KB or Web
→ Rewrite if needed
→ Retry
→ Generate grounded answer
The system therefore controls what to do next based on its current state.

5. Main Technology Stack
   Layer Technology Purpose
   Agent workflow LangGraph Stateful routing and conditional decisions
   LLM Groq Routing, grading, rewriting, answer generation
   Embeddings HuggingFace all-MiniLM-L6-v2 Local 384-dimensional embeddings
   Vector DB Pinecone Private enterprise knowledge base
   External search Tavily Fallback when company KB is insufficient
   API FastAPI Backend and REST endpoints
   Frontend HTML/CSS/JavaScript Employee-facing interface
   Audit SQLite Basic decision-path logging
   Packaging Docker Reproducible deployment
6. Project Structure
   FDE_Agentic_RAG_IT_Copilot/
   │
   ├── app/
   │ ├── api/
   │ │ └── routes.py # Chat, health and ingestion APIs
   │ │
   │ ├── core/
   │ │ ├── config.py # Environment configuration
   │ │ └── logging.py # Logging configuration
   │ │
   │ ├── rag/
   │ │ ├── state.py # LangGraph state + structured decisions
   │ │ ├── vectorstore.py # Pinecone + embeddings
   │ │ └── workflow.py # Complete Agentic RAG graph
   │ │
   │ ├── services/
   │ │ ├── audit.py # SQLite query audit
   │ │ └── ingestion.py # PDF/TXT/MD/DOCX loading + chunking
   │ │
   │ └── main.py # FastAPI application
   │
   ├── data/
   │ └── sample_kb/
   │ ├── company_it_handbook.md
   │ └── service_desk_runbook.md
   │
   ├── static/
   │ ├── css/style.css
   │ └── js/app.js
   │
   ├── templates/
   │ └── index.html
   │
   ├── tests/
   │ └── test_ingestion.py
   │
   ├── uploads/
   ├── .env.example
   ├── Dockerfile
   ├── ingest_sample_kb.py
   ├── requirements.txt
   ├── run.py
   └── README.md
