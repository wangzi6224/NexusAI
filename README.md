<div align="center">

# NexusAI

<img src="https://img.shields.io/badge/Python-3.11%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
<img src="https://img.shields.io/badge/FastAPI-0.136-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI">
<img src="https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black" alt="React">
<img src="https://img.shields.io/badge/PostgreSQL-pgvector-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL">
<img src="https://img.shields.io/badge/Ollama-Local%20LLM-black?style=for-the-badge&logo=ollama&logoColor=white" alt="Ollama">
<img src="https://img.shields.io/badge/DeepSeek-API-FF6B35?style=for-the-badge" alt="DeepSeek">

<br/>

<img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="License">
<img src="https://img.shields.io/badge/build-passing-brightgreen?style=flat-square" alt="Build">
<img src="https://img.shields.io/badge/RAG-Hybrid%20Retrieval-purple?style=flat-square" alt="RAG">
<img src="https://img.shields.io/badge/Agent-Tool%20Augmented-orange?style=flat-square" alt="Agent">
<img src="https://img.shields.io/badge/Streaming-SSE-blue?style=flat-square" alt="Streaming">
<img src="https://img.shields.io/badge/Embedding-Multilingual-red?style=flat-square" alt="Embedding">

<br/><br/>

**A production-ready AI backend platform with RAG, Agent, and multi-LLM support.**


[English](#-overview) · [中文文档](./README_CN.md) · [API Docs](#-api-reference) · [Quick Start](#-quick-start)

</div>

---

## 📖 Overview

**NexusAI** is a full-stack AI application platform that combines a high-performance FastAPI backend with a modern React frontend. It provides an intelligent conversational experience powered by **Retrieval-Augmented Generation (RAG)**, a **Tool-Augmented Agent** system, and seamless multi-LLM provider support.


### ✨ Key Features

| Feature | Description |
|---|---|
| 🤖 **Multi-LLM Routing** | Switch between local Ollama models and DeepSeek cloud API via config |
| 📚 **Hybrid RAG** | Vector search + BM25 keyword search with RRF fusion and BGE reranking |
| 🛠️ **Tool-Augmented Agent** | Multi-step reasoning loop with `list_docs`, `search_docs`, `read_doc` tools |
| 💬 **Multi-turn Conversations** | Persistent conversation history with context summarization |
| 📄 **Document Management** | Upload, chunk, embed, and index Markdown & plain-text documents |
| 🔄 **Streaming Output** | Real-time Server-Sent Events (SSE) for token-by-token streaming |
| 🔍 **Agent Trace** | Full observability of agent reasoning steps and tool calls |
| 🎛️ **Smart Mode Routing** | Auto-dispatch to `chat`, `rag`, or `agent` mode based on query intent |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        NexusAI Platform                         │
├─────────────────┬───────────────────────────────────────────────┤
│   Frontend      │  React 18 + TypeScript + Ant Design X         │
│   (web/)        │  Tailwind CSS · SSE streaming · Trace Drawer  │
├─────────────────┼───────────────────────────────────────────────┤
│   API Layer     │  FastAPI · Routers: chat / rag / agent /       │
│   (src/app/api) │  assistant / conversations / documents         │
├─────────────────┼───────────────────────────────────────────────┤
│                 │  ┌──────────┐  ┌──────────┐  ┌────────────┐  │
│   Services      │  │  Agent   │  │   RAG    │  │ Assistant  │  │
│                 │  │  Loop    │  │ Hybrid   │  │Orchestrator│  │
│                 │  │  Planner │  │Retriever │  │ ModeRouter │  │
│                 │  └────┬─────┘  └────┬─────┘  └─────┬──────┘  │
│                 │       │             │               │          │
│                 │  ┌────▼─────────────▼───────────────▼──────┐  │
│                 │  │           LLM Factory                    │  │
│                 │  │   OllamaProvider  │  DeepSeekProvider    │  │
│                 │  └──────────────────────────────────────────┘  │
├─────────────────┼───────────────────────────────────────────────┤
│   Data Layer    │  PostgreSQL + pgvector · Embedding (E5-base)  │
│                 │  BGE Reranker · Chunk Splitter · Doc Loader   │
└─────────────────┴───────────────────────────────────────────────┘
```

---

## 🔬 Core Components

### 🧠 RAG Pipeline

NexusAI implements a **three-stage hybrid RAG** pipeline:

1. **Query Rewriting** — Reformulates the user query for better retrieval coverage
2. **Hybrid Retrieval** — Combines dense vector search (pgvector) with sparse BM25 keyword search, fused using **Reciprocal Rank Fusion (RRF)**
3. **Reranking** — `BAAI/bge-reranker-base` cross-encoder reranks top candidates before LLM generation

```
User Query
    │
    ▼
Query Rewriter ──► Vector Retrieval (pgvector, top-30)
                         +
                   Keyword Retrieval (BM25, top-30)
                         │
                    RRF Fusion (top-20)
                         │
                    BGE Reranker (top-5)
                         │
                    LLM Generation
```

### 🛠️ Agent Loop

The agent uses a **ReAct-style** step loop with a configurable max-step limit:

```
User Question
    │
    ▼
Planner (LLM) ──► Tool Selection ──► Tool Execution ──► Observation
    ▲                                                        │
    └────────────────────────────────────────────────────────┘
    (repeat until DONE or max_steps reached)
    │
    ▼
Final Answer
```

**Available Tools:**
- `list_docs` — List all documents in the knowledge base
- `search_docs` — Semantic search across the knowledge base
- `read_doc` — Read full content of a specific document

### 🔄 Assistant Orchestrator

The `AssistantOrchestrator` is the unified streaming entry point. It routes requests via `ModeRouter`:

| Mode | Behavior |
|------|----------|
| `chat` | Direct multi-turn LLM conversation |
| `agent` | Tool-augmented reasoning with knowledge base access |
| `auto` | Rule-based routing to `chat` or `agent` based on query analysis |

---

## 🛠️ Tech Stack

**Backend**
- **Runtime**: Python 3.11+ / FastAPI / Uvicorn
- **LLM Providers**: Ollama (local) · DeepSeek API (cloud)
- **Embedding**: `intfloat/multilingual-e5-base` (768-dim, multilingual)
- **Reranker**: `BAAI/bge-reranker-base` (cross-encoder)
- **Database**: PostgreSQL 15+ with `pgvector` extension
- **Config**: Pydantic Settings + `.env` file

**Frontend**
- **Framework**: React 18 + TypeScript
- **UI Library**: Ant Design X (AI-first components)
- **Styling**: Tailwind CSS
- **Build**: Vite / pnpm

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11 – 3.12
- PostgreSQL 15+ with pgvector extension
- [Ollama](https://ollama.com) (for local LLM)
- Node.js 18+ and pnpm (for frontend)

### 1. Backend Setup

```bash
# Clone the repository
git clone https://github.com/wangzi6224/NexusAI.git
cd NexusAI

# Install Python dependencies (recommended: uv)
uv pip install -r requirements.txt

# Copy and configure environment variables
cp .env.example .env
# Edit .env to set your POSTGRES_*, OLLAMA_MODEL, LLM_PROVIDER, etc.
```

### 2. Database Initialization

```bash
# Create the database and apply schema
psql -U <your_user> -d <your_db> -f sql/init.sql
```

### 3. Pull a Local Model (Ollama)

```bash
ollama serve
ollama pull gemma4:e2b   # or any other supported model
```

### 4. Start the Backend

```bash
uv run -m src.app.main --reload
# API is available at http://localhost:8000
# Swagger docs at http://localhost:8000/docs
```

### 5. Start the Frontend

```bash
cd web
pnpm install
pnpm run dev
# Frontend available at http://localhost:8001
```

---

## 📡 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/chat` | Synchronous chat |
| `POST` | `/api/chat/stream` | Streaming chat (SSE) |
| `POST` | `/api/assistant/{id}/stream` | Assistant stream (auto mode routing) |
| `POST` | `/api/rag/ask` | Single-turn RAG Q&A |
| `GET` | `/api/rag/search` | Retrieve relevant document chunks |
| `POST` | `/api/agent/chat` | Agent multi-step reasoning |
| `GET` | `/api/agent/runs/{run_id}` | Agent trace details |
| `POST` | `/api/documents/upload` | Upload a document |
| `GET` | `/api/documents` | List all documents |
| `POST` | `/api/conversations` | Create a conversation |
| `GET` | `/api/conversations/{id}/messages` | Fetch conversation history |
| `GET` | `/api/health` | Health check |

> 📘 Full interactive API documentation is available at `/docs` (Swagger UI) and `/redoc`.

---

## ⚙️ Configuration

Key environment variables (see `.env`):

```env
# LLM Provider: "ollama" or "deepseek"
LLM_PROVIDER=ollama

# Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=gemma4:e2b

# DeepSeek
DEEPSEEK_API_KEY=your_api_key
DEEPSEEK_MODEL=deepseek-v4-flash

# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=ai_backend
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password

# RAG
RERANKER_ENABLED=true
EMBEDDING_MODEL=intfloat/multilingual-e5-base
```

---

## 📂 Project Structure

```
NexusAI/
├── src/app/
│   ├── api/
│   │   └── routers/          # FastAPI route handlers
│   ├── services/
│   │   ├── agent/            # Agent loop, planner, prompt builder
│   │   ├── rag/              # Hybrid retriever, reranker, query rewriter
│   │   ├── assistant/        # Orchestrator, mode router, run store
│   │   ├── llm/              # Ollama & DeepSeek provider implementations
│   │   ├── embedding/        # Sentence-transformer embedding service
│   │   └── tools/            # Agent tool registry and implementations
│   ├── schemas/              # Pydantic request/response models
│   └── config.py             # Centralized settings (pydantic-settings)
├── web/                      # React + TypeScript frontend
├── sql/                      # Database schema and migrations
├── tests/                    # Pytest test suite
└── docs/                     # Learning notes and documentation
```

---

## 🤝 Contributing

Contributions are welcome! Please open an issue or submit a pull request.

---

## 📄 License

This project is licensed under the **MIT License**.

---

<div align="center">

📖 **[查看中文文档 →](./README_CN.md)**

*Built with ❤️ using FastAPI · Ollama · pgvector · React*

</div>
