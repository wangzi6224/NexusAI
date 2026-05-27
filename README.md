# my_python_project

一个基于 FastAPI 的 AI 聊天后端，集成 Ollama 模型调用、RAG 文档检索、向量搜索和前端开发服务器。

## 项目架构概览

- `src/app/`
  - `main.py`: 启动脚本，负责启动前端 dev server 和后端 `uvicorn` 服务。
  - `server.py`: FastAPI 应用入口，配置 CORS、静态文件和路由。
  - `api/routes.py`: REST API 总路由入口，只负责聚合各业务路由模块。
  - `api/routers/`: 按业务域拆分的 API 路由，包括基础状态、聊天、会话、文档、Embedding 和 RAG。
  - `services/`: 核心业务层，包含聊天服务、会话管理、文档处理、文本切分、向量存储、Embedding 和 RAG 相关逻辑。
  - `services/rag/`: RAG 子域逻辑，包括检索、混合检索、rerank、query rewrite 和调试接口支撑。
  - `services/agent/`: Agent 对话流程、规划器、状态和 prompt 构建逻辑。
  - `services/llm/`: LLM provider 抽象和 Ollama 调用实现。
  - `services/embedding/`: Embedding provider 抽象和 sentence-transformers 实现。
  - `services/tools/`: Agent 可调用工具集合。
  - `config.py`: 环境配置管理，使用 `pydantic-settings` 读取 `.env` 环境变量。
  - `paths.py`: 项目路径定义，包括静态目录、数据目录和前端目录。
  - `static/`: 后端静态资源目录。
  - `data/`: 本地运行时数据目录（已配置为 Git 忽略，仅保留本地数据）。

- `web/`
  - 前端源码目录，包含 `package.json`、`pnpm` 配置和 React/Umi 前端应用。

- `docs/`
  - 本地笔记与文档目录，已设置为 Git 忽略，用于本地记录学习和项目文档。

- `tests/`
  - 单元测试目录。

## 依赖安装

### Python 环境

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

如果使用 `pyproject.toml`，也可以运行：

```bash
python3 -m pip install .
```

### 前端依赖

```bash
cd web
pnpm install
```

## 运行方式

### 启动后端 + 前端开发服务器

推荐命令：

```bash
python -m src.app.main
```

该命令将：

- 启动 `pnpm run dev` 前端开发服务器
- 启动后端 FastAPI 服务，默认监听 `127.0.0.1:8000`

### 单独启动后端

```bash
uvicorn src.app.server:app --reload --host 127.0.0.1 --port 8000
```

## 配置项（`.env`）

可在项目根目录创建 `.env`，覆盖默认配置：

```env
APP_ENV=development
APP_LOG_LEVEL=INFO
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=gemma4:e2b
OLLAMA_TIMEOUT=1200
OLLAMA_KEEP_ALIVE=5m
CHAT_HISTORY_PATH=chat_history.json
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=ai_backend
POSTGRES_USER=wangzilong
POSTGRES_PASSWORD=ai_backend_password
EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
EMBEDDING_BATCH_SIZE=5000
EMBEDDING_DIMENSION=384
```

## 主要功能

- 聊天功能
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

- `data/`：运行时生成的数据文件目录，包含聊天历史、会话、文档元数据、Embedding 状态等。
- `docs/`：项目文档目录，当前已设置为 Git 忽略，仅保留本地内容。

## 贡献与开发

- 推荐使用 `python -m src.app.main` 快速调试前后端。
- 修改后端代码后，`uvicorn --reload` 会自动热重载。
- 前端开发时，`web/` 目录使用 `pnpm` 进行依赖管理。
- 如果需要在远端托管，确保 `.env` 中的敏感信息不提交到版本控制。

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
│   │       └── rag.py
│   ├── services/
│   │   ├── agent/
│   │   ├── embedding/
│   │   ├── llm/
│   │   ├── rag/
│   │   └── tools/
│   ├── static/
│   ├── data/
│   └── config.py
├── web/
│   ├── package.json
│   ├── tsconfig.json
│   └── src/
├── docs/
└── tests/
```
