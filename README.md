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
<img src="https://img.shields.io/badge/Memory--System-Two%2DTier-red?style=flat-square" alt="Memory System">

<br/><br/>

**A production-ready full-stack AI platform with Hybrid RAG, Tool-Augmented Agent, Two-Tier Memory System, and Multi-LLM Routing.**


[中文文档](./README_CN.md) · [API Docs](#-api-reference) · [Quick Start](#-quick-start) · [Architecture](#-architecture)

</div>

---

## 📖 Overview

**NexusAI** is a production-ready full-stack AI application platform that combines a high-performance FastAPI backend with a modern React frontend. It provides an intelligent conversational experience powered by:

- **Hybrid Retrieval-Augmented Generation (RAG)** — Vector search + BM25 keyword retrieval with RRF fusion and BGE cross-encoder reranking
- **Tool-Augmented Agent System** — ReAct-style multi-step reasoning loop with configurable planners (LLM-based or rule-based)
- **Two-Tier Memory System** — Short-term conversation state + Long-term persistent memory with semantic deduplication
- **Multi-LLM Routing** — Seamless switching between local Ollama models and DeepSeek cloud API
- **Streaming Output** — Real-time Server-Sent Events (SSE) for token-by-token streaming across all modes

### ✨ Key Features

| Feature | Description |
|---|---|
| 🤖 **Multi-LLM Routing** | Switch between local Ollama models and DeepSeek cloud API via config or runtime selection |
| 📚 **Hybrid RAG** | Dense vector (pgvector HNSW) + sparse BM25 keyword search, RRF fusion, MMR diversity, BGE reranking |
| 🛠️ **Tool-Augmented Agent** | ReAct-style loop with `list_docs`, `search_docs`, `read_doc` tools; LLM or rule-based planner |
| 💬 **Multi-turn Conversations** | Persistent conversation history with context summarization and sliding window |
| 📄 **Document Management** | Upload, chunk (Markdown-aware), embed, and index Markdown & plain-text documents |
| 🔄 **Streaming Output** | Real-time SSE streaming for chat, RAG, agent, and assistant modes |
| 🔍 **Agent Trace** | Full observability: planner decisions, tool calls, observations, step details, events |
| 🧠 **Two-Tier Memory** | Short-term conversation state (goal, facts, constraints) + Long-term semantic memory with deduplication |
| 🎛️ **Smart Mode Routing** | Rule-based + LLM-based auto-dispatch to `chat`, `rag`, `agent`, or `mcp` mode |
| 📊 **Health Monitoring** | Real-time backend health check with model status display in UI |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        NexusAI Platform                          │
├─────────────────┬───────────────────────────────────────────────┤
│   Frontend       │  React 18 + TypeScript + Ant Design X          │
│    (web/)        │  Tailwind CSS · SSE Streaming · Trace Drawer   │
├─────────────────┼───────────────────────────────────────────────┤
│   API Layer      │  FastAPI · Routers: chat / rag / agent /       │
│  (src/app/api)   │  assistant / conversations / documents         │
├─────────────────┼───────────────────────────────────────────────┤
│                  │   ┌──────────┐   ┌──────────┐   ┌──────────┐  │
│   Service        │   │  Agent   │   │  Hybrid  │   │ Assistant│  │
│                  │   │  Loop    │   │  RAG     │   │ Orchestr.│  │
│                  │   │ Planner  │   │ Retriever│   │ ModeRouter│  │
│                  │   └────┬─────┘   └────┬─────┘   └────┬─────┘  │
│                  │        │               │                │       │
│                  │   ┌────▼───────────────▼────────────────▼───┐  │
│                  │   │          LLM Factory                      │  │
│                  │   │   OllamaProvider  │  DeepSeekProvider    │  │
│                  │   └──────────────────────────────────────────┘  │
│                  │   ┌──────────────┐   ┌──────────────────────┐  │
│                  │   │ Memory System │   │ Document Pipeline    │  │
│                  │   │ Short/Long-t. │   │ Load → Chunk → Embed │  │
│                  │   └──────────────┘   └──────────────────────┘  │
├─────────────────┼───────────────────────────────────────────────┤
│   Data Layer     │  PostgreSQL + pgvector (HNSW index)            │
│                  │  BGE Reranker · Chunk Splitter · Doc Loader    │
│                  │  9 Tables: docs, chunks, conversations,        │
│                  │  messages, agent_runs, assistant_runs,         │
│                  │  memory_items, conversation_states, history    │
└─────────────────┴───────────────────────────────────────────────┘
```

---

## 🔬 Core Components

### 🧠 Hybrid RAG Pipeline

NexusAI implements a **five-stage hybrid RAG** pipeline:

1. **Query Rewriting** — Reformulates the user query for better retrieval coverage using LLM-based context awareness
2. **Parallel Retrieval** — Dense vector search (pgvector HNSW, top-30) + sparse BM25 keyword search (top-30) execute in parallel
3. **RRF Fusion** — Reciprocal Rank Fusion merges results from both retrieval sources (top-20)
4. **MMR Diversity** — Maximal Marginal Relevance filters duplicates and improves result diversity
5. **BGE Reranking** — `BAAI/bge-reranker-base` cross-encoder reranks top candidates before LLM generation

```
User Query
     │
     ▼
Query Rewriter ──► Vector Retrieval (pgvector HNSW, top-30)
                          +
                   Keyword Retrieval (BM25, top-30)
                          │
                    RRF Fusion (top-20)
                          │
                     MMR Filter (diversity)
                          │
                    BGE Reranker (top-5)
                          │
                    LLM Generation
```

**Retrieval Modes:**
| Mode | Description |
|------|-------------|
| `vector_rerank` | Vector search → Reranking (standard mode) |
| `hybrid` | Vector + BM25 → RRF Fusion → MMR → Reranking |

### 🛠️ Agent System

The agent uses a **ReAct-style** step loop with configurable planner backends:

```
User Question
     │
     ▼
Planner (LLM / Rule-based) ──► Tool Selection ──► Tool Execution ──► Observation
     ▲                                                              │
     └────────────────────────────────────────────────────────────┘
     (repeat until DONE or max_steps reached)
     │
     ▼
Final Answer Generator
```

**Planner Types:**
| Type | Description |
|------|-------------|
| `llm` | LLM-driven planning with JSON schema validation and rule-based fallback |
| `rule` | Deterministic rule-based planning for predictable scenarios |

**Available Tools:**
| Tool | Description |
|------|-------------|
| `list_docs` | List all documents in the knowledge base |
| `search_docs` | Semantic search across the knowledge base with configurable top-k and score threshold |
| `read_doc` | Read full content of a specific document with max character limit |

**Safety Features:**
- Tool whitelist enforcement
- JSON schema validation for tool arguments
- Duplicate tool call detection and blocking
- Result length limiting
- Prompt injection protection

### 🔄 Assistant Orchestrator

The `AssistantOrchestrator` is the unified streaming entry point. It combines chat, agent, and memory into a single coherent stream:

**Smart Mode Routing (Two-Layer):**

| Layer | Behavior |
|-------|----------|
| **Rule-Based Router** | Fast deterministic routing for small talk, explicit RAG requests, explicit agent requests, MCP requests |
| **LLM-Based Router** | Falls back to LLM classification when rules are inconclusive |

**Supported Modes:**
| Mode | Behavior |
|------|----------|
| `chat` | Direct multi-turn LLM conversation with context window |
| `rag` | Single-turn RAG Q&A with hybrid retrieval |
| `agent` | Tool-augmented reasoning with knowledge base access |
| `mcp` | External tool/system integration (reserved) |
| `auto` | Rule + LLM based auto-dispatch to optimal mode |

**Streaming Events:**
The assistant stream emits rich SSE events for full UI traceability:

| Event | Description |
|-------|-------------|
| `assistant_start` | Assistant response begins |
| `route_decision` | Auto-routing decision details |
| `short_term_memory_loaded` | Conversation state loaded |
| `long_term_memory_retrieval_start` | Long-term memory search begins |
| `long_term_memory_item` | Individual long-term memory item retrieved |
| `tool_call_start` / `tool_call_end` | Tool call lifecycle |
| `delta` | Model token streaming chunk |
| `assistant_end` | Assistant response completes |
| `error` | Error event |
| `done` | Stream termination marker |

### 🧠 Two-Tier Memory System

NexusAI implements a sophisticated memory system with two distinct tiers:

#### Short-Term Memory (Per-Conversation)
- **Structure**: `conversation_states` table — one state per conversation
- **Content**: Current goal, current topic, confirmed facts, confirmed constraints, user preferences, open questions, task state
- **Extraction**: LLM-based `ConversationStateExtractor` processes each turn to update the state
- **Storage**: JSONB fields in PostgreSQL

#### Long-Term Memory (Cross-Conversation)
- **Structure**: `memory_items` table — persistent across conversations
- **Types**: `user_profile`, `semantic`, `episodic`, `tool_preference`, `project`
- **Extraction**: LLM-based extractor identifies memorable content from user/assistant turns
- **Scoring**: Composite score = similarity (55%) + importance (20%) + confidence (15%) + recency (7%) + access frequency (3%)
- **Deduplication**: Semantic deduplication prevents storing duplicate or highly similar memories
- **Policy**: Filters out sensitive content, temporary information, low-confidence items, and short content

**Memory Lifecycle:**
```
User/Assistant Turn
     │
     ▼
Extract Candidates (LLM)
     │
     ▼
Apply Policy Filter
     │
     ├─→ Too short? → Skip
     ├─→ Low confidence? → Skip
     ├─→ Sensitive content? → Skip
     └─→ Passes filter?
          │
          ▼
     Deduplication Check
          │
          ├─→ Exact match? → Update existing
          ├─→ Highly similar? → Update existing
          └─→ New? → Insert as new memory
```

### 📄 Document Pipeline

```
Upload File (Markdown / Plain Text)
     │
     ▼
Validate & Extract Text
     │
     ▼
Chunk Splitter (Markdown-aware)
     │
     ├─► Heading-based section extraction
     ├─► Paragraph-level splitting
     └─► Max 1000 chars per chunk, 120 char overlap
     │
     ▼
Store in PostgreSQL (documents + document_chunks)
     │
     ▼
Embedding Service (batch process)
     │
     └─► intfloat/multilingual-e5-base → 768-dim vectors
     │
     ▼
Store Vectors in pgvector (HNSW index)
```

---

## 🛠️ Tech Stack

**Backend**
| Category | Technology |
|----------|------------|
| Runtime | Python 3.11+ / FastAPI 0.136 / Uvicorn 0.45 |
| LLM Providers | Ollama (local) · DeepSeek API (cloud, OpenAI-compatible) |
| Embedding | `intfloat/multilingual-e5-base` (768-dim, multilingual) |
| Reranker | `BAAI/bge-reranker-base` (cross-encoder, FlagEmbedding) |
| Database | PostgreSQL 15+ with `pgvector` extension (HNSW index) |
| Text Search | `pg_trgm` for fuzzy matching, `tsvector` for BM25 |
| Config | Pydantic Settings + `.env` file |
| Testing | Pytest 9.0 |

**Frontend**
| Category | Technology |
|----------|------------|
| Framework | React 18 + TypeScript 5.9 |
| UI Library | Ant Design X 2.3 (AI-first components) |
| Boilerplate | Umi Max 4.6 |
| Styling | Tailwind CSS 3 · Custom CSS variables |
| Build | Vite / pnpm |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11 – 3.12
- PostgreSQL 15+ with `pgvector` and `pg_trgm` extensions
- [Ollama](https://ollama.com) (for local LLM inference)
- Node.js 18+ and pnpm (for frontend, optional — backend can run standalone)

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

The `init.sql` creates 9 tables:
- `documents` — Source file records
- `document_chunks` — Text chunks with embeddings and full-text search vectors
- `conversations` — Conversation metadata and summaries
- `messages` — Message timeline per conversation
- `chat_history` — Per-request Q&A audit log
- `agent_runs` — Agent execution summaries
- `agent_steps` — Per-agent-step details
- `agent_events` — Agent trace events for observability
- `assistant_runs` — Assistant orchestrator call records
- `conversation_states` — Short-term memory per conversation
- `memory_items` — Cross-conversation long-term memory

Plus essential indexes including **HNSW vector index**, **GIN full-text indexes**, and **GIN trgm indexes**.

### 3. Pull a Local Model (Ollama)

```bash
ollama serve
ollama pull gemma4:e2b    # or any other supported model
```

### 4. Start the Backend

```bash
uv run -m src.app.main --reload
# API is available at http://localhost:8000
# Swagger docs at http://localhost:8000/docs
```

The `src.app.main` module provides smart port management:
- Automatically releases port 8000 if occupied by a previous NexusAI process
- Launches the frontend dev server in the background
- Starts the FastAPI server with hot-reload

### 5. Start the Frontend (Optional)

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
| `POST` | `/api/chat` | Synchronous chat — returns complete response |
| `POST` | `/api/chat/stream` | Streaming chat (SSE) — token-by-token output |
| `POST` | `/api/assistant/{id}/stream` | Assistant stream — auto mode routing + memory + agent |
| `POST` | `/api/rag/ask` | Single-turn RAG Q&A with hybrid retrieval |
| `GET` | `/api/rag/search` | Retrieve relevant document chunks |
| `POST` | `/api/agent/chat` | Agent multi-step reasoning with tool calls |
| `GET` | `/api/agent/runs/{run_id}` | Agent trace details (steps + events) |
| `GET` | `/api/agent/conversations/{id}/runs` | List agent runs for a conversation |
| `POST` | `/api/documents/upload` | Upload a document (multipart form) |
| `GET` | `/api/documents` | List all documents |
| `GET` | `/api/documents/{id}` | Get document detail |
| `GET` | `/api/documents/{id}/chunks` | List document chunks |
| `DELETE` | `/api/documents/{id}` | Delete a document and its chunks |
| `POST` | `/api/conversations` | Create a conversation |
| `GET` | `/api/conversations` | List all conversations |
| `GET` | `/api/conversations/{id}/messages` | Fetch conversation history |
| `DELETE` | `/api/conversations/{id}` | Delete a conversation |
| `POST` | `/api/models/select` | Select default LLM provider and model |
| `GET` | `/api/models` | Get available models info |
| `GET` | `/api/health` | Health check |

> 📘 Full interactive API documentation is available at `/docs` (Swagger UI) and `/redoc`.

### Request / Response Examples

**Chat (Synchronous):**
```json
// POST /api/chat
{ "message": "What is React?" }

// Response
{
  "answer": "React is a JavaScript library for building user interfaces...",
  "provider": "ollama",
  "model": "gemma4:e2b",
  "latency_ms": 1234,
  "usage": {
    "prompt_tokens": 20,
    "completion_tokens": 150,
    "total_tokens": 170
  }
}
```

**Assistant Stream (SSE):**
```json
// POST /api/assistant/{conversation_id}/stream
{ "message": "Search docs about React hooks" }

// Events:
// assistant_start → route_decision → tool_call_start → delta* → tool_call_end → done
```

---

## ⚙️ Configuration

Key environment variables (see `.env`):

```env
# ─── LLM Provider ─────────────────────────────
# "ollama" or "deepseek"
LLM_PROVIDER=ollama

# ─── Ollama Configuration ──────────────────────
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=gemma4:e2b
OLLAMA_TIMEOUT=1200
OLLAMA_KEEP_ALIVE=5m

# ─── DeepSeek Configuration ────────────────────
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_API_KEY=your_api_key
DEEPSEEK_MODEL=deepseek-v4-flash
DEEPSEEK_TIMEOUT=120
DEEPSEEK_THINKING_ENABLED=false

# ─── PostgreSQL ────────────────────────────────
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=ai_backend
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password

# ─── Embedding ─────────────────────────────────
EMBEDDING_MODEL=intfloat/multilingual-e5-base
EMBEDDING_BATCH_SIZE=1500
EMBEDDING_DIMENSION=768

# ─── RAG Configuration ─────────────────────────
RERANKER_ENABLED=true
RERANKER_MODEL=BAAI/bge-reranker-base
RERANKER_USE_FP16=false
RAG_CANDIDATE_K=30
RAG_RERANK_TOP_N=5
RAG_MAX_RERANK_CONTENT_CHARS=1200
RAG_DEFAULT_RETRIEVAL_MODE=vector_rerank
RAG_VECTOR_TOP_K=30
RAG_KEYWORD_TOP_K=30
RAG_FUSION_TOP_K=20
RAG_RRF_K=60
RAG_MMR_ENABLED=true
RAG_MMR_LAMBDA=0.7

# ─── Agent Configuration ───────────────────────
AGENT_PLANNER_TYPE=llm
```

---

## 📂 Project Structure

```
NexusAI/
├── src/app/
│    ├── api/
│    │    ├── routers/           # FastAPI route handlers
│    │    │    ├── agent.py      # Agent chat & trace endpoints
│    │    │    ├── assistant.py  # Assistant orchestrator stream
│    │    │    ├── chat.py       # Chat (sync + stream) endpoints
│    │    │    ├── conversations.py # Conversation CRUD
│    │    │    ├── documents.py  # Document upload/list/delete
│    │    │    ├── embeddings.py # Embedding management
│    │    │    ├── history_models.py # History & model selection
│    │    │    └── base.py       # Base router configuration
│    │    ├── routes.py          # Router aggregation
│    │    └── exception_handlers.py # Global error handling
│    ├── services/
│    │    ├── agent/             # Agent loop, planner, prompt builder
│    │    │    ├── agent_service.py   # Main agent service
│    │    │    ├── loop.py            # ReAct-style execution loop
│    │    │    ├── planner.py         # Rule-based planner
│    │    │    ├── llm_planner.py     # LLM-driven planner
│    │    │    ├── planner_parser.py  # JSON schema validation
│    │    │    ├── planner_prompt_builder.py # Planner prompts
│    │    │    ├── decision_schema.py   # Tool call JSON schema
│    │    │    └── state.py             # Agent state models
│    │    ├── assistant/         # Orchestrator, mode router, run store
│    │    │    ├── orchestrator.py      # Unified streaming entry
│    │    │    ├── mode_router.py       # Rule + LLM routing
│    │    │    ├── llm_router.py        # LLM-based mode classifier
│    │    │    ├── llm_route_prompt.py  # Routing prompts
│    │    │    ├── run_store.py         # Assistant run persistence
│    │    │    └── event.py             # SSE event type definitions
│    │    ├── rag/               # Hybrid retriever, reranker, query rewriter
│    │    │    ├── hybrid_retriever.py  # Vector + BM25 fusion
│    │    │    ├── retriever.py         # Standard vector + rerank
│    │    │    ├── keyword_retriever.py # BM25 keyword search
│    │    │    ├── rank_fusion.py       # RRF algorithm
│    │    │    ├── mmr.py               # Maximal Marginal Relevance
│    │    │    ├── reranker.py          # BGE cross-encoder wrapper
│    │    │    ├── reranker_provider.py # FlagEmbedding provider
│    │    │    ├── query_rewriter.py    # LLM-based query rewrite
│    │    │    ├── prompt_builder.py    # RAG system prompts
│    │    │    └── conversation_rag_service.py # Conversational RAG
│    │    ├── memory/            # Two-tier memory system
│    │    │    ├── short_term_store.py      # Conversation states
│    │    │    ├── short_term_schemas.py    # State models
│    │    │    ├── short_term_builder.py    # Context builder
│    │    │    ├── long_term_store.py       # Persistent memory
│    │    │    ├── long_term_schemas.py     # Memory models
│    │    │    ├── long_term_retriever.py   # Semantic search
│    │    │    ├── long_term_writer.py      # LLM extraction + storage
│    │    │    ├── long_term_ranker.py      # Composite scoring
│    │    │    ├── long_term_deduper.py     # Deduplication
│    │    │    └── long_term_policy.py      # Storage policies
│    │    ├── tools/             # Agent tool registry & implementations
│    │    │    ├── base.py              # Tool ABC
│    │    │    ├── registry.py          # Whitelist enforcement
│    │    │    ├── list_docs.py         # List knowledge base docs
│    │    │    ├── search_docs.py       # Semantic search tool
│    │    │    ├── read_doc.py          # Read full document
│    │    │    └── safety.py            # Result limiting
│    │    ├── llm/               # LLM provider implementations
│    │    │    ├── base.py              # LLMProvider ABC
│    │    │    ├── factory.py           # Provider selection
│    │    │    ├── ollama_provider.py   # Ollama REST API
│    │    │    └── deepseek_provider.py # OpenAI-compatible API
│    │    ├── embedding/         # Embedding service
│    │    │    └── sentence_transformer_provider.py # SentenceTransformers
│    │    ├── agent_trace_store.py   # Agent run/step/event persistence
│    │    ├── conversation_store.py  # Conversation/message persistence
│    │    ├── document_store.py      # Document/chunk persistence
│    │    ├── vector_store.py        # pgvector operations
│    │    ├── keyword_store.py       # BM25 keyword search
│    │    ├── chunk_splitter.py      # Markdown-aware text splitting
│    │    ├── document_loader.py     # File type validation & loading
│    │    ├── context_builder.py     # Context window assembly
│    │    ├── summarizer.py          # Conversation summary generation
│    │    ├── chat_service.py        # Chat business logic
│    │    ├── conversation_service.py # Conversation business logic
│    │    ├── document_service.py    # Document upload & processing
│    │    ├── embedding_service.py   # Embedding batch processing
│    │    ├── health_service.py      # Health check logic
│    │    ├── history_service.py     # History audit logging
│    │    ├── model_service.py       # Model selection logic
│    │    └── rag/                   # (symlink to services/rag)
│    ├── schemas/               # Pydantic request/response models
│    │    ├── schemas.py         # Core API models
│    │    ├── agent.py           # Agent-specific models
│    │    └── assistant.py       # Assistant-specific models
│    ├── config.py              # Centralized Settings (pydantic-settings)
│    ├── db.py                  # Database connection helper
│    ├── paths.py               # Path utilities
│    ├── main.py                # Entry point with port management
│    ├── server.py              # FastAPI app with CORS & static files
│    ├── exceptions.py          # Custom exception classes
│    ├── logger.py              # Logging configuration
│    ├── prompts.py             # Chat system prompts
│    └── runtime_config.py      # Runtime provider selection
├── web/                       # React + TypeScript frontend
│    ├── src/
│    │    ├── components/
│    │    │    ├── ChatLayout/         # Main layout with sidebar
│    │    │    ├── ChatView/           # Chat container
│    │    │    ├── ChatMessageList/    # Message rendering
│    │    │    ├── ChatInputBar/       # Input with mode selector
│    │    │    ├── ChatSenderInput/    # Enhanced sender input
│    │    │    ├── Sidebar/            # Conversation list sidebar
│    │    │    ├── WelcomeScreen/      # Landing screen
│    │    │    ├── MarkdownContent/    # Rendered markdown output
│    │    │    ├── ToolCallTimeline/   # Agent tool call visualization
│    │    │    ├── TraceDrawer/        # Agent trace detail panel
│    │    │    └── FeedbackFooter/     # Message feedback UI
│    │    ├── contexts/
│    │    │    └── ChatContext.tsx     # Global chat state
│    │    ├── services/               # API client layer
│    │    ├── pages/                  # Route pages
│    │    └── components/             # Reusable UI components
├── sql/                       # Database schema and migrations
│    └── init.sql               # Full schema with indexes
├── tests/                     # Pytest test suite
├── scripts/                   # Utility scripts
│    └── debug_chunk_splitter.py # Chunk debugging
└── docs/                      # Learning notes and documentation
```

---

## 🗄️ Database Schema Overview

The database consists of **11 tables** organized into functional groups:

### Document Management
| Table | Purpose |
|-------|---------|
| `documents` | Source file metadata (filename, type, status, chunk count) |
| `document_chunks` | Text chunks with embeddings, headings, full-text search vectors |

### Conversations & Messages
| Table | Purpose |
|-------|---------|
| `conversations` | Conversation metadata, summaries, model/provider info |
| `messages` | Per-conversation message timeline (user/assistant roles) |
| `chat_history` | Per-request Q&A audit log with latency tracking |

### Agent Observability
| Table | Purpose |
|-------|---------|
| `agent_runs` | Agent execution summaries (status, step count, latency, final answer) |
| `agent_steps` | Per-step details (tool name, arguments, result, success) |
| `agent_events` | Fine-grained trace events for UI visualization |

### Memory System
| Table | Purpose |
|-------|---------|
| `assistant_runs` | Assistant orchestrator call records with mode and trace |
| `conversation_states` | Short-term memory per conversation (goal, facts, constraints) |
| `memory_items` | Cross-conversation long-term memory with embeddings and scoring |

### Key Indexes
- **HNSW** (`idx_document_chunks_embedding_hnsw`) — Fast vector similarity search
- **GIN tsvector** (`idx_document_chunks_search_vector`) — BM25 full-text search
- **GIN trgm** (`idx_document_chunks_content_trgm`) — Fuzzy text matching
- **Composite** (`idx_agent_runs_conversation_id_created_at`) — Agent runs by conversation

---

## 🤝 Contributing

Contributions are welcome! Please open an issue or submit a pull request.

### Development Guidelines
- Follow the existing code style and naming conventions
- Add tests for new features when applicable
- Update documentation for API changes
- Ensure all LLM providers work correctly after changes

---

## 📄 License

This project is licensed under the **MIT License**.
