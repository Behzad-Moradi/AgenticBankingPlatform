# Agentic Banking Platform

A full-stack reference implementation of an AI-assisted banking experience built with FastAPI, LangGraph, PostgreSQL, Weaviate, React, and TypeScript.

The platform demonstrates how a conversational interface can safely coordinate specialised banking agents, authenticated data access, retrieval-augmented generation (RAG), document verification, and human approval steps. It is designed as a development and demonstration environment—not as a production banking system.

## Overview

The application presents customers with a single conversational banking assistant. A LangGraph workflow classifies each request and directs it to the appropriate specialist while preserving the conversation state under an authenticated, customer-scoped thread.

Customers can use the interface to:

- Register and authenticate with email and password.
- Ask about their accounts, balances, and recent transactions.
- Search bank policies, fees, products, and documentation through a cited RAG knowledge base.
- Investigate card activity and request a card freeze.
- Open an everyday or savings account through a guided workflow.
- Upload a driver licence for identity verification.
- Approve customer-facing actions and simulate staff approval through human-in-the-loop controls.

## Architecture

```mermaid
flowchart LR
    UI[React + TypeScript UI] -->|JWT-authenticated REST| API[FastAPI API]
    API --> GRAPH[LangGraph Orchestrator]

    GRAPH --> CHAT[General Assistant]
    GRAPH --> ACCOUNTS[Account Specialist]
    GRAPH --> KNOWLEDGE[Knowledge Specialist]
    GRAPH --> CARDS[Card Security Specialist]
    GRAPH --> OPENING[Account Opening Workflow]

    ACCOUNTS --> DB[(PostgreSQL)]
    CARDS --> DB
    OPENING --> DB
    KNOWLEDGE --> VECTOR[(Weaviate)]
    VECTOR --> DOCS[Bank Knowledge Documents]

    CARDS --> HITL[Human Confirmation]
    OPENING --> VERIFY[Licence Extraction and Verification]
    OPENING --> HITL
```

### Request lifecycle

1. The customer authenticates and receives a time-limited JWT.
2. The frontend creates a conversation `thread_id` and includes it with every chat request.
3. The backend scopes that identifier to the authenticated customer before accessing LangGraph state.
4. The intent router selects a specialist agent or workflow.
5. Specialists use customer-scoped tools, PostgreSQL data, or the Weaviate knowledge base as required.
6. Sensitive actions pause at a LangGraph interrupt and continue only after an explicit approve or reject decision.

## Core capabilities

### Specialised agent routing

The orchestration graph separates general conversation from account enquiries, knowledge retrieval, card security, and account opening. Each specialist receives a deliberately limited role and toolset, reducing the risk of unrelated actions or invented banking data.

### Retrieval-augmented banking knowledge

Banking documents are divided into overlapping chunks, embedded with OpenAI embeddings, and stored in Weaviate. Retrieval combines semantic vector search with keyword matching, followed by reranking. Answers include the source filename, page where available, and chunk index returned by the knowledge workflow.

The ingestion pipeline supports:

- Markdown knowledge documents.
- Text-based PDF documents.
- Multimodal PDF pages containing tables, diagrams, screenshots, or scanned content.

### Account-opening workflow

Account opening is implemented as a stateful, multi-step workflow:

1. Select an everyday or savings account.
2. Check whether the customer already holds that account type.
3. Collect the customer’s full name, date of birth, address, and phone number.
4. Request a driver licence upload.
5. Extract and compare licence details with the submitted application.
6. Present the application for customer confirmation.
7. Pause for a simulated staff approval or rejection.
8. Create the account only after approval.

### Card security and human approval

The card-security specialist can inspect the authenticated customer’s cards and recent card transactions. A freeze request resolves the selected card, pauses for confirmation, and updates the card only when the request is approved. Card ownership is checked again at the database operation boundary.

### Authentication and customer isolation

- Passwords are stored as secure hashes using `pwdlib` with its recommended configuration.
- Access tokens are signed JWTs with configurable expiry.
- Protected endpoints resolve the current customer from the token.
- LangGraph thread IDs are prefixed with the authenticated customer ID.
- Account, card, and transaction tools filter records by the authenticated customer.

## Technology stack

| Layer | Technology |
|---|---|
| Frontend | React, TypeScript, Vite |
| API | FastAPI, Pydantic |
| Agent orchestration | LangGraph, LangChain |
| Language models | OpenAI chat models and embeddings |
| Relational data | PostgreSQL, SQLAlchemy, Alembic |
| Vector search | Weaviate hybrid retrieval |
| Authentication | JWT bearer tokens, password hashing |
| Document processing | PyPDF, PyMuPDF, multimodal model extraction |
| Quality tooling | Pytest, Ruff, mypy, ESLint, TypeScript |

## Repository structure

```text
AgenticBankingPlatform/
├── backend/
│   ├── alembic/                 # Database migrations
│   ├── data/knowledge/          # RAG source documents
│   ├── scripts/                 # Ingestion, seed, and evaluation utilities
│   ├── src/backend/
│   │   ├── agents/              # Router, specialists, graph, and workflows
│   │   ├── api/                 # Authentication and chat endpoints
│   │   ├── core/                # Configuration and security
│   │   ├── db/                  # SQLAlchemy session and metadata
│   │   ├── models/              # Customer, account, card, and transaction models
│   │   ├── rag/                 # Loaders, retrieval, reranking, and generation
│   │   ├── schemas/             # Pydantic API contracts
│   │   ├── services/            # Document extraction services
│   │   └── tools/               # Customer-scoped agent tools
│   └── tests/
├── frontend/
│   ├── src/
│   │   ├── components/          # Authentication, chat, upload, and HITL UI
│   │   ├── services/            # API and browser-session services
│   │   └── types/               # TypeScript API and conversation contracts
│   └── vite.config.ts
└── README.md
```

## Prerequisites

Before starting the project, install and configure:

- Python 3.11
- [`uv`](https://docs.astral.sh/uv/)
- Node.js and npm
- PostgreSQL
- A locally accessible Weaviate instance
- An OpenAI API key

The default application configuration expects the FastAPI service at `http://127.0.0.1:8000`, the frontend at `http://localhost:5173`, and Weaviate on its standard local connection settings.

## Backend setup

From the repository root:

```bash
cd backend
cp .env.example .env
uv sync
```

Complete `backend/.env` with the required configuration:

```env
ENVIRONMENT=development
DATABASE_URL=postgresql+psycopg://username:password@localhost:5432/database_name
OPENAI_API_KEY=your_openai_api_key
JWT_SECRET_KEY=replace_with_a_long_random_secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ALLOWED_ORIGINS=["http://localhost:5173","http://127.0.0.1:5173"]
```

Create the PostgreSQL database, then apply the migrations:

```bash
uv run alembic upgrade head
```

With Weaviate running, ingest the bundled knowledge documents:

```bash
uv run python scripts/ingest_knowledge.py
```

Start the API:

```bash
uv run uvicorn backend.main:app --reload
```

The backend is then available at:

- API: `http://127.0.0.1:8000`
- Interactive documentation: `http://127.0.0.1:8000/docs`
- Health check: `http://127.0.0.1:8000/health`

## Frontend setup

In a separate terminal, from the repository root:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`.

During development, Vite proxies `/api` requests to `http://127.0.0.1:8000`. To use a different API location, create `frontend/.env` and set:

```env
VITE_API_BASE_URL=https://api.example.com
```

If the frontend is served from a different origin, include that exact origin in the backend’s `CORS_ALLOWED_ORIGINS` setting.

## Using the application

1. Open the frontend and select **Create account**.
2. Register a customer profile; the frontend signs in automatically after successful registration.
3. Use the suggested prompts or enter a banking request.
4. Keep the same conversation open while completing a stateful workflow.
5. For account opening, upload a JPEG, PNG, or PDF driver licence when requested.
6. Use the approve or reject controls when the graph returns a human-in-the-loop interrupt.

Newly registered customers do not automatically receive sample accounts, cards, or transactions. Development seed scripts are available under `backend/scripts/`; review their configured customer identifiers and prerequisites before running them.

## API summary

| Method | Endpoint | Purpose | Authentication |
|---|---|---|---|
| `POST` | `/auth/register` | Register a customer profile | No |
| `POST` | `/auth/token` | Exchange email and password for a JWT | No |
| `POST` | `/chat` | Send a message within a conversation thread | Bearer token |
| `POST` | `/chat/resume` | Approve or reject an interrupted workflow | Bearer token |
| `POST` | `/chat/account-opening/document` | Upload a driver licence for verification | Bearer token |
| `GET` | `/health` | Check API availability | No |

The repository also contains customer CRUD endpoints used during backend development. Consult the generated OpenAPI documentation for their current request and response schemas.

## Development and verification

Run backend tests and static checks from `backend/`:

```bash
uv run pytest
uv run ruff check .
uv run mypy src
```

Run frontend checks from `frontend/`:

```bash
npm run lint
npm run build
```

RAG evaluation and retrieval diagnostics are available in `backend/scripts/`. Some scripts call external models or require a populated Weaviate collection and should therefore be run with the relevant services available.

## Development considerations

- LangGraph currently uses an in-memory checkpointer, so conversation state is cleared when the backend process restarts and is not shared across multiple API instances.
- The document-verification implementation demonstrates AI-assisted extraction and deterministic field comparison; it is not a substitute for a regulated identity-verification service.
- Human-in-the-loop controls are exposed in the demonstration frontend so both approval paths can be tested. A production system should separate customer and staff authorisation surfaces.
- Model responses can be imperfect. Banking actions should remain constrained by deterministic validation, ownership checks, audit logging, and appropriately authorised human review.
- Secrets and real customer data must never be committed to the repository or added to the demonstration knowledge base.

## Intended use

This project is suitable for architecture demonstrations, agent-workflow experimentation, RAG evaluation, and full-stack prototyping. Before any real-world financial deployment, it would require production-grade identity and access management, persistent and encrypted workflow state, comprehensive audit trails, observability, rate limiting, security testing, regulatory controls, and formal operational review.
