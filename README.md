# NexusAI

基于 FastAPI 构建的本地 AI 后端服务，集成 Ollama 大模型调用、混合检索 RAG 问答、向量化文档管理、多轮会话管理、Agent 工具调用，并配套 Umi Max + Ant Design X 前端。

## 技术栈

**后端**

- Python 3.11 / 3.12
- FastAPI 0.136.0 + Uvicorn 0.45.0
- PostgreSQL + pgvector（向量存储）+ pg_trgm（全文检索）
- Ollama（本地 LLM 调用）
- sentence-transformers / intfloat/multilingual-e5-base（Embedding，768 维）
- BAAI/bge-reranker-base（交叉编码精排，基于 FlagEmbedding）
- pydantic-settings（配置管理）
- psycopg 3（PostgreSQL 驱动）

**前端**

- Umi Max 4.6.26 + React + TypeScript 5.9.3
- Ant Design 5.x + @ant-design/x（AI 对话组件）+ @ant-design/x-markdown
- Tailwind CSS
- pnpm 包管理

## 项目结构

```
NexusAI/
├── src/app/
│   ├── main.py                  # 一键启动入口：同时启动前端 dev 服务与后端 uvicorn
│   ├── server.py                # FastAPI 应用实例，配置 CORS、静态挂载、路由注册
│   ├── config.py                # pydantic-settings 全量配置，读取 .env
│   ├── paths.py                 # 项目路径常量（静态目录、上传目录、数据目录等）
│   ├── db.py                    # psycopg 3 数据库连接工厂
│   ├── runtime_config.py        # 运行时可变配置（当前选中模型），持久化到 data/runtime_config.json
│   ├── conversation_store.py    # 会话 / 消息的 PostgreSQL CRUD
│   ├── document_store.py        # 文档元数据与分块的 JSON 持久化
│   ├── api/
│   │   ├── routes.py            # 路由聚合入口
│   │   ├── exception_handlers.py
│   │   └── routers/
│   │       ├── base.py          # 首页 / 健康检查
│   │       ├── chat.py          # 同步聊天 / 流式聊天
│   │       ├── conversations.py # 多轮会话管理
│   │       ├── documents.py     # 文档上传 / 查询 / 删除
│   │       ├── embeddings.py    # Embedding 测试 / 向量化
│   │       ├── history_models.py# 聊天历史 / 模型查询与切换
│   │       ├── rag.py           # RAG 检索 / 问答 / 带会话历史 RAG
│   │       └── agent.py         # Agent 多步工具调用对话
│   ├── services/
│   │   ├── llm/
│   │   │   └── ollama_provider.py   # Ollama HTTP 流式调用封装
│   │   ├── embedding/
│   │   │   └── sentence_transformer_provider.py  # SentenceTransformer 向量化
│   │   ├── rag/
│   │   │   ├── hybrid_retriever.py  # 混合检索主流程（向量 + 关键词 + RRF + MMR + Rerank）
│   │   │   ├── keyword_retriever.py # pg_trgm 全文关键词检索
│   │   │   ├── rank_fusion.py       # Reciprocal Rank Fusion 融合排序
│   │   │   ├── mmr.py               # MMR 多样性筛选
│   │   │   ├── reranker.py          # RAG 精排业务层
│   │   │   ├── reranker_provider.py # BGE Reranker 模型调用
│   │   │   ├── retrieval_mode.py    # 检索模式枚举（vector_rerank / hybrid）
│   │   │   ├── rag_service.py       # RAG 无会话问答服务
│   │   │   ├── conversation_rag_service.py  # RAG 带会话历史问答服务
│   │   │   └── query_rewriter.py    # 查询改写
│   │   ├── agent/
│   │   │   ├── agent_service.py     # Agent 入口，初始化工具注册表和 LLM
│   │   │   ├── loop.py              # ReAct 多步 Agent 执行循环
│   │   │   ├── planner.py           # 步骤规划
│   │   │   ├── prompt_builder.py    # Agent 系统提示构建
│   │   │   └── state.py             # Agent 执行状态
│   │   ├── tools/
│   │   │   ├── registry.py          # 工具注册表
│   │   │   ├── list_docs.py         # 工具：列出文档
│   │   │   ├── search_docs.py       # 工具：文档语义搜索
│   │   │   └── read_doc.py          # 工具：读取文档原文
│   │   ├── vector_store.py          # pgvector 向量写入 / 相似度检索
│   │   ├── chat_service.py          # 简单聊天（无会话）服务
│   │   ├── conversation_service.py  # 多轮会话业务逻辑
│   │   ├── document_service.py      # 文档上传、切分、状态管理
│   │   ├── embedding_service.py     # 文档向量化调度
│   │   ├── chunk_splitter.py        # 文档切分策略
│   │   ├── context_builder.py       # RAG 上下文组装
│   │   ├── summarizer.py            # 会话摘要生成
│   │   ├── model_service.py         # Ollama 模型列表查询与切换
│   │   └── keyword_store.py         # 关键词索引辅助
│   ├── schemas/                     # Pydantic 请求 / 响应 Schema
│   ├── static/                      # 内置静态前端（build 产物）
│   └── data/                        # 运行时数据（uploads、runtime_config.json）
├── web/                             # 前端源码（Umi Max）
├── sql/init.sql                     # 数据库初始化 DDL
├── tests/                           # 单元测试
└── scripts/                         # 调试脚本
```

## 核心功能

### 聊天

- `POST /chat`：同步聊天，调用当前 Ollama 模型返回完整回复
- `POST /chat/stream`：流式聊天，通过 Server-Sent Events 返回增量输出

### 多轮会话管理

- 会话存储于 PostgreSQL `conversations` / `messages` 表
- 支持创建会话、查看会话列表与详情、获取消息历史
- 支持同步与流式发送消息、手动触发摘要更新
- 上下文预览接口，用于调试上下文窗口内容

### 文档管理与 Embedding

- 上传文档，提取文本并切分为 chunk 存入 `document_chunks` 表
- 对单个或全量文档调用 SentenceTransformer 生成 768 维向量，写入 pgvector
- 查询文档列表、详情、分块内容、Embedding 状态

### RAG 检索增强问答

检索流程（`hybrid` 模式）：

1. 向量检索：查询 embedding 与 pgvector 余弦相似度搜索
2. 关键词检索：基于 PostgreSQL pg_trgm 的全文匹配
3. RRF 融合排序：Reciprocal Rank Fusion 合并两路结果
4. MMR 多样性筛选：去除冗余候选，提升结果多样性
5. BGE 精排：BAAI/bge-reranker-base 交叉编码二次排序

`vector_rerank` 模式跳过关键词检索和 RRF，直接对向量结果精排。

API：

- `POST /rag/search`：只返回检索结果，不生成回答（调试用）
- `POST /rag/ask`：RAG 问答，不绑定会话历史
- `POST /rag/conversation/ask`：RAG 问答，结合多轮会话历史

### Agent 工具调用

基于 ReAct 模式的多步 Agent，内置工具：

- `list_docs`：列出当前系统中的所有文档
- `search_docs`：对文档库执行语义检索
- `read_doc`：读取指定文档原文

API：`POST /agent/chat?conversation_id=<id>`

### 模型管理

- `GET /models`：查询 Ollama 可用模型列表
- `POST /models/select`：切换当前使用的模型，结果持久化到 `data/runtime_config.json`

### 健康检查

- `GET /health`：返回后端服务状态

## 数据库初始化

依赖 PostgreSQL 并启用 `vector` 和 `pg_trgm` 扩展：

```bash
psql -U <user> -d <dbname> -f sql/init.sql
```

主要表结构：

| 表名 | 说明 |
|---|---|
| `documents` | 文档元数据（文件名、类型、状态、字符数等） |
| `document_chunks` | 文档分块（内容、embedding 向量、全文索引 tsvector） |
| `conversations` | 多轮会话（标题、摘要、模型、状态） |
| `messages` | 会话消息（role、content、metadata） |
| `chat_history` | 简单聊天接口的历史记录 |

## 依赖安装

### Python 环境

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

或通过 `pyproject.toml` 安装（支持 editable 模式）：

```bash
pip install -e .
```

### 前端依赖

```bash
cd web
pnpm install
```

## 运行方式

### 同时启动后端与前端开发服务器（推荐）

```bash
python -m src.app.main
```

该命令会：

1. 检测并清理 8000 端口的旧后端进程
2. 在 `web/` 目录启动前端开发服务器（`pnpm run dev`，端口 8001）
3. 启动后端 FastAPI 服务，监听 `127.0.0.1:8000`

### 单独启动后端

```bash
uvicorn src.app.server:app --reload --host 127.0.0.1 --port 8000
```

### 访问地址

- 后端 API：`http://localhost:8000`
- 前端开发服务器：`http://localhost:8001`
- 内置静态页面：`http://localhost:8000/`
- FastAPI 交互文档：`http://localhost:8000/docs`

## 配置项（`.env`）

在项目根目录创建 `.env` 文件，可覆盖以下默认值：

```env
# 应用
APP_ENV=development
APP_LOG_LEVEL=INFO

# Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=gemma4:e2b
OLLAMA_TIMEOUT=1200
OLLAMA_KEEP_ALIVE=5m

# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=ai_backend
POSTGRES_USER=wangzilong
POSTGRES_PASSWORD=ai_backend_password

# Embedding
EMBEDDING_MODEL=intfloat/multilingual-e5-base
EMBEDDING_BATCH_SIZE=1500
EMBEDDING_DIMENSION=768

# Reranker
RERANKER_ENABLED=true
RERANKER_MODEL=BAAI/bge-reranker-base
RERANKER_USE_FP16=false

# RAG 检索参数
RAG_CANDIDATE_K=30
RAG_RERANK_TOP_N=5
RAG_MAX_RERANK_CONTENT_CHARS=1200

# 聊天历史
CHAT_HISTORY_PATH=chat_history.json
```

## 运行测试

```bash
pytest tests/
```

## API 主要接口

以下接口由 `src/app/api/routers` 中路由模块提供：

- 聊天
  - `POST /chat`
  - `POST /chat/stream`
  - `GET /history`
  - `POST /history/clear`
- 模型管理
  - `GET /models`
  - `POST /model/select`
- 会话管理
  - `POST /conversations`
  - `GET /conversations`
  - `GET /conversations/{conversation_id}`
  - `GET /conversations/{conversation_id}/messages`
  - `POST /conversations/{conversation_id}/messages`
  - `POST /conversations/{conversation_id}/messages/stream`
  - `GET /conversations/{conversation_id}/context-preview`
  - `POST /conversations/{conversation_id}/summary`
- 文档与向量检索
  - `POST /documents/upload`
  - `GET /documents`
  - `GET /documents/{document_id}`
  - `GET /documents/{document_id}/chunks`
  - `DELETE /documents/{document_id}`
  - `POST /documents/{document_id}/embed`
  - `POST /documents/embed-all`
  - `POST /embeddings/test`
  - `GET /documents/{document_id}/embedding-status`
  - `POST /embeddings/search-debug`
  - `POST /rag/search`
  - `POST /rag/ask`

## 本地数据说明

- `data/`：运行时生成的本地数据目录，用于存储聊天历史、会话记录、文档元数据、Embedding 状态等。
- `docs/`：本地文档与学习笔记目录，通常用于项目备忘和调试记录，不作为运行期依赖。

## 开发建议

- 推荐使用 `python -m src.app.main` 同时调试前后端。
- 后端代码修改后，可使用 `uvicorn --reload` 实现热重载。
- 前端开发时，通过 `web/` 目录中的 `pnpm` 进行依赖管理和构建。
- 部署时请务必将 `.env` 中敏感信息排除在版本控制之外。

## 目录结构

```text
.
├── pyproject.toml
├── README.md
├── requirements.txt
├── src/app/
│   ├── main.py
│   ├── server.py
│   ├── api/
│   │   ├── routes.py
│   │   └── routers/
│   │       ├── base.py
│   │       ├── chat.py
│   │       ├── history_models.py
│   │       ├── conversations.py
│   │       ├── documents.py
│   │       ├── embeddings.py
│   │       ├── rag.py
│   │       └── agent.py
│   ├── services/
│   │   ├── agent/
│   │   ├── embedding/
│   │   ├── llm/
│   │   ├── rag/
│   │   └── tools/
│   ├── static/
│   ├── data/
│   ├── config.py
│   └── paths.py
├── web/
│   ├── package.json
│   ├── pnpm-lock.yaml
│   ├── tsconfig.json
│   └── src/
├── docs/
└── tests/
```
