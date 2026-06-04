<div align="center">

# NexusAI

<img src="https://img.shields.io/badge/Python-3.11%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
<img src="https://img.shields.io/badge/FastAPI-0.136-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI">
<img src="https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black" alt="React">
<img src="https://img.shields.io/badge/PostgreSQL-pgvector-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL">
<img src="https://img.shields.io/badge/Ollama-本地模型-black?style=for-the-badge&logo=ollama&logoColor=white" alt="Ollama">
<img src="https://img.shields.io/badge/DeepSeek-云端API-FF6B35?style=for-the-badge" alt="DeepSeek">

<br/>

<img src="https://img.shields.io/badge/许可证-MIT-green?style=flat-square" alt="License">
<img src="https://img.shields.io/badge/构建-通过-brightgreen?style=flat-square" alt="Build">
<img src="https://img.shields.io/badge/RAG-混合检索-purple?style=flat-square" alt="RAG">
<img src="https://img.shields.io/badge/Agent-工具增强-orange?style=flat-square" alt="Agent">
<img src="https://img.shields.io/badge/流式输出-SSE-blue?style=flat-square" alt="Streaming">
<img src="https://img.shields.io/badge/记忆系统-双层架构-red?style=flat-square" alt="Memory System">

<br/><br/>

**生产就绪的全栈 AI 应用平台 —— 混合 RAG、工具 Agent、双层记忆系统、多 LLM 灵活切换。**


[English README](./README.md) · [快速开始](#-快速开始) · [API 参考](#-api-参考) · [架构说明](#-系统架构)

</div>

---

## 📖 项目简介

**NexusAI** 是一个生产就绪的全栈 AI 应用平台，集成了高性能 FastAPI 后端与现代 React 前端。平台以以下核心能力为基础，提供智能、流畅的对话体验：

- **混合检索增强生成（Hybrid RAG）** — 向量检索 + BM25 关键词检索，RRF 融合排序，BGE 交叉编码器精排
- **工具增强 Agent 系统** — ReAct 风格多步推理循环，支持 LLM 驱动或规则驱动的规划器
- **双层记忆系统** — 短期会话状态 + 长期跨会话语义记忆，支持语义去重与综合评分
- **多 LLM 路由** — 在本地 Ollama 模型与 DeepSeek 云端 API 之间无缝切换
- **流式输出** — 基于 Server-Sent Events (SSE) 的逐 token 实时流式输出，覆盖所有模式

### ✨ 核心特性

| 功能 | 说明 |
|---|---|
| 🤖 **多 LLM 路由** | 通过配置或运行时选择在本地 Ollama 模型与 DeepSeek 云端 API 之间切换 |
| 📚 **混合 RAG** | 稠密向量（pgvector HNSW）+ 稀疏 BM25 关键词检索，RRF 融合，MMR 去重多样性，BGE 精排 |
| 🛠️ **工具增强 Agent** | ReAct 风格多步推理循环，内置 `list_docs`、`search_docs`、`read_doc` 三类工具；支持 LLM/规则双规划器 |
| 💬 **多轮对话** | 持久化会话历史，支持上下文摘要压缩与滑动窗口 |
| 📄 **文档管理** | 上传、Markdown 感知切片、向量化并索引 Markdown 与纯文本文档 |
| 🔄 **流式输出** | 基于 SSE 的实时流式输出，覆盖 chat、rag、agent、assistant 所有模式 |
| 🔍 **Agent 追踪** | 完整可观测性：规划器决策、工具调用、观察结果、步骤详情、事件时间线 |
| 🧠 **双层记忆系统** | 短期会话状态（目标、事实、约束）+ 长期跨会话语义记忆，支持语义去重与综合评分 |
| 🎛️ **智能模式路由** | 规则引擎 + LLM 分类器，自动分发至 `chat`、`rag`、`agent` 或 `mcp` 模式 |
| 📊 **健康监控** | 实时后端健康检查，前端 UI 显示模型状态 |

---

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        NexusAI 平台                               │
├─────────────────┬───────────────────────────────────────────────┤
│   前端层          │  React 18 + TypeScript + Ant Design X          │
│    (web/)         │  Tailwind CSS · SSE 流式 · Trace 抽屉           │
├─────────────────┼───────────────────────────────────────────────┤
│   API 层          │  FastAPI · 路由: chat / rag / agent /           │
│   (src/app/api)   │  assistant / conversations / documents          │
├─────────────────┼───────────────────────────────────────────────┤
│                   │    ┌──────────┐   ┌──────────┐   ┌──────────┐  │
│   服务层          │    │  Agent   │   │ 混合 RAG │   │ Assistant│  │
│                   │    │  循环    │   │  检索器  │   │  编排器  │  │
│                   │    │  规划器  │   │          │   │  模式路由│  │
│                   │    └────┬─────┘   └────┬─────┘   └────┬─────┘  │
│                   │         │                │                 │     │
│                   │    ┌────▼───────────────▼─────────────────▼──┐  │
│                   │    │        LLM 工厂                             │  │
│                   │    │   OllamaProvider   │  DeepSeekProvider    │  │
│                   │    └──────────────────────────────────────────┘  │
│                   │    ┌──────────────┐   ┌──────────────────────┐  │
│                   │    │  记忆系统     │   │  文档处理流水线        │  │
│                   │    │  短期/长期    │   │  加载 → 切片 → 嵌入    │  │
│                   │    └──────────────┘   └──────────────────────┘  │
├─────────────────┼───────────────────────────────────────────────┤
│   数据层          │  PostgreSQL + pgvector (HNSW 索引)              │
│                   │  BGE 重排器 · Markdown 感知切片器 · 文档加载器    │
│                   │  11 张表: 文档、分块、会话、消息、                  │
│                   │  Agent 运行记录、Assistant 运行记录、             │
│                   │  长期记忆、短期记忆状态、对话历史                    │
└─────────────────┴───────────────────────────────────────────────┘
```

---

## 🔬 核心模块详解

### 🧠 RAG 管道

NexusAI 实现了**五阶段混合 RAG** 管道：

1. **查询改写** — 基于 LLM 的上下文感知，对用户问题进行语义扩展，提升召回覆盖率
2. **并行检索** — 稠密向量检索（pgvector HNSW, top-30）与稀疏 BM25 关键词检索（top-30）并行执行
3. **RRF 融合** — 互惠排名融合（Reciprocal Rank Fusion）合并两个检索源的结果（top-20）
4. **MMR 去重** — 最大边际相关性算法过滤重复内容，提升结果多样性
5. **BGE 精排** — 使用 `BAAI/bge-reranker-base` 交叉编码器对候选结果精排，再交给 LLM 生成最终回答

```
用户问题
     │
     ▼
查询改写器 ──► 向量检索（pgvector HNSW, top-30）
                        +
                关键词检索（BM25, top-30）
                        │
                 RRF 融合（top-20）
                        │
                  MMR 去重（多样性）
                        │
                 BGE 精排器（top-5）
                        │
                 LLM 生成回答
```

**检索模式：**
| 模式 | 说明 |
|------|------|
| `vector_rerank` | 向量检索 → 重排序（标准模式） |
| `hybrid` | 向量 + BM25 → RRF 融合 → MMR → 重排序（完整混合模式） |

### 🛠️ Agent 系统

Agent 采用 **ReAct 风格**的步骤循环，支持两种规划器后端：

```
用户问题
     │
     ▼
规划器（LLM / 规则驱动） ──► 工具选择 ──► 工具执行 ──► 观察结果
     ▲                                                    │
     └────────────────────────────────────────────────────┘
     （循环直到 DONE 或达到最大步数）
     │
     ▼
最终回答生成器
```

**规划器类型：**
| 类型 | 说明 |
|------|------|
| `llm` | LLM 驱动规划，JSON Schema 校验，规则兜底 |
| `rule` | 确定性规则驱动规划，适用于可预测场景 |

**内置工具列表：**

| 工具名 | 说明 |
|--------|------|
| `list_docs` | 列出知识库中的所有文档 |
| `search_docs` | 在知识库中执行语义搜索，支持自定义 top-k 和分数阈值 |
| `read_doc` | 读取指定文档的完整内容，支持最大字符数限制 |

**安全特性：**
- 工具白名单强制校验
- 工具参数 JSON Schema 校验
- 重复工具调用检测与拦截
- 结果长度限制
- Prompt 注入防护

### 🔄 Assistant 编排器

`AssistantOrchestrator` 是统一的流式入口，将对话、Agent 和记忆系统整合为一个连贯的流：

**智能模式路由（双层架构）：**

| 层级 | 行为 |
|------|------|
| **规则引擎** | 快速确定性路由：闲聊、明确 RAG 请求、明确 Agent 请求、MCP 请求 |
| **LLM 分类器** | 规则无法确定时，回退到 LLM 进行分类 |

**支持的模式：**
| 模式 | 行为 |
|------|------|
| `chat` | 直接多轮 LLM 对话，带上下文窗口 |
| `rag` | 单轮 RAG 问答，混合检索 |
| `agent` | 工具增强推理，可访问知识库 |
| `mcp` | 外部工具/系统集成（预留） |
| `auto` | 规则 + LLM 自动分发至最优模式 |

**流式事件：**
Assistant 流式输出发射丰富的 SSE 事件，支持完整的 UI 追踪可视化：

| 事件 | 说明 |
|------|------|
| `assistant_start` | Assistant 响应开始 |
| `route_decision` | 自动路由决策详情 |
| `short_term_memory_loaded` | 短期会话状态加载完成 |
| `long_term_memory_retrieval_start` | 长期记忆检索开始 |
| `long_term_memory_item` | 单条长期记忆项检索结果 |
| `tool_call_start` / `tool_call_end` | 工具调用生命周期 |
| `delta` | LLM token 流式片段 |
| `assistant_end` | Assistant 响应完成 |
| `error` | 错误事件 |
| `done` | 流结束标记 |

### 🧠 双层记忆系统

NexusAI 实现了复杂的双层记忆架构：

#### 短期记忆（单会话级）
- **存储结构**：`conversation_states` 表 — 每个会话一条状态记录
- **内容**：当前目标、当前主题、已确认事实、已确认约束、用户偏好、待解决问题、任务状态
- **提取方式**：LLM 驱动的 `ConversationStateExtractor` 处理每轮对话以更新状态
- **存储方式**：PostgreSQL JSONB 字段

#### 长期记忆（跨会话级）
- **存储结构**：`memory_items` 表 — 跨会话持久化存储
- **记忆类型**：`user_profile`（用户画像）、`semantic`（语义知识）、`episodic`（情景记忆）、`tool_preference`（工具偏好）、`project`（项目信息）
- **提取方式**：LLM 驱动的记忆提取器从用户/助手对话中识别值得记忆的内容
- **综合评分**：相似度 (55%) + 重要性 (20%) + 置信度 (15%) + 时效性 (7%) + 访问频率 (3%)
- **语义去重**：防止存储重复或高度相似的记忆内容
- **策略过滤**：过滤掉敏感信息、临时性内容、低置信度项和过短内容

**记忆生命周期：**
```
用户/助手对话轮次
      │
      ▼
LLM 提取候选记忆
      │
      ▼
应用策略过滤器
      │
      ├─→ 内容太短？ → 跳过
      ├─→ 置信度低？ → 跳过
      ├─→ 敏感内容？ → 跳过
      └─→ 通过过滤？
           │
           ▼
     语义去重检查
           │
           ├─→ 完全匹配？ → 更新现有记忆
           ├─→ 高度相似？ → 更新现有记忆
           └─→ 全新内容？ → 插入为新记忆
```

### 📄 文档处理流水线

```
上传文件（Markdown / 纯文本）
      │
      ▼
验证并提取文本
      │
      ▼
Markdown 感知切片器
      │
      ├─► 基于标题的章节提取
      ├─► 段落级切分
      └─► 每块最多 1000 字符，重叠 120 字符
      │
      ▼
存储至 PostgreSQL（documents + document_chunks）
      │
      ▼
批量向量化服务
      │
      └─► intfloat/multilingual-e5-base → 768 维向量
      │
      ▼
将向量存储至 pgvector（HNSW 索引）
```

---

## 🛠️ 技术栈

### 后端

| 分类 | 技术 |
|------|------|
| 运行时 | Python 3.11+ · FastAPI 0.136 · Uvicorn 0.45 |
| LLM 提供商 | Ollama（本地）· DeepSeek API（云端，OpenAI 兼容）|
| 向量嵌入 | `intfloat/multilingual-e5-base`（768 维，多语言）|
| 重排器 | `BAAI/bge-reranker-base`（交叉编码器，FlagEmbedding）|
| 数据库 | PostgreSQL 15+ + `pgvector` 扩展（HNSW 索引）|
| 文本搜索 | `pg_trgm` 模糊匹配，`tsvector` BM25 |
| 配置管理 | Pydantic Settings + `.env` 文件 |
| 测试框架 | Pytest 9.0 |

### 前端

| 分类 | 技术 |
|------|------|
| 框架 | React 18 + TypeScript 5.9 |
| UI 组件库 | Ant Design X 2.3（AI 原生组件）|
| 脚手架 | Umi Max 4.6 |
| 样式 | Tailwind CSS 3 · 自定义 CSS 变量 |
| 构建工具 | Vite / pnpm |

---

## 🚀 快速开始

### 环境要求

- Python 3.11 – 3.12
- PostgreSQL 15+（含 `pgvector` 和 `pg_trgm` 扩展）
- [Ollama](https://ollama.com)（本地 LLM 推理）
- Node.js 18+ 与 pnpm（前端，可选 — 后端可独立运行）

### 第一步：后端配置

```bash
# 克隆仓库
git clone https://github.com/wangzi6224/NexusAI.git
cd NexusAI

# 安装 Python 依赖（推荐使用 uv）
uv pip install -r requirements.txt

# 复制并配置环境变量
cp .env.example .env
# 编辑 .env，设置 POSTGRES_*、OLLAMA_MODEL、LLM_PROVIDER 等
```

### 第二步：初始化数据库

```bash
# 创建数据库并执行初始化 SQL
psql -U <你的用户名> -d <数据库名> -f sql/init.sql
```

`init.sql` 将创建 **11 张表**：
- `documents` — 源文件记录
- `document_chunks` — 文本分块（含向量、标题、全文搜索向量）
- `conversations` — 会话元数据和摘要
- `messages` — 会话消息时间线
- `chat_history` — 单轮问答审计日志
- `agent_runs` — Agent 执行汇总
- `agent_steps` — Agent 单步详情
- `agent_events` — Agent 追踪事件
- `assistant_runs` — Assistant 编排器调用记录
- `conversation_states` — 短期会话记忆
- `memory_items` — 跨会话长期记忆

同时创建关键索引：**HNSW 向量索引**、**GIN 全文索引**、**GIN trgm 索引**。

### 第三步：拉取本地模型（Ollama）

```bash
ollama serve
ollama pull gemma4:e2b     # 或其他支持的模型
```

### 第四步：启动后端服务

```bash
uv run -m src.app.main --reload
# API 服务：http://localhost:8000
# Swagger 文档：http://localhost:8000/docs
```

`src.app.main` 模块提供智能端口管理：
- 自动检测并释放被旧 NexusAI 进程占用的 8000 端口
- 后台启动前端开发服务器
- 启动带热重载的 FastAPI 服务

### 第五步：启动前端（可选）

```bash
cd web
pnpm install
pnpm run dev
# 前端地址：http://localhost:8001
```

---

## 📡 API 参考

| 方法 | 路径 | 说明 |
|------|------|------|
| `POST` | `/api/chat` | 同步聊天 — 返回完整回答 |
| `POST` | `/api/chat/stream` | 流式聊天（SSE）— 逐 token 输出 |
| `POST` | `/api/assistant/{id}/stream` | Assistant 流式接口 — 自动路由 + 记忆 + Agent |
| `POST` | `/api/rag/ask` | 单轮 RAG 问答，混合检索 |
| `GET` | `/api/rag/search` | 检索相关文档分块 |
| `POST` | `/api/agent/chat` | Agent 多步推理对话 |
| `GET` | `/api/agent/runs/{run_id}` | Agent 追踪详情（步骤 + 事件） |
| `GET` | `/api/agent/conversations/{id}/runs` | 列出会话的 Agent 运行记录 |
| `POST` | `/api/documents/upload` | 上传文档（multipart form） |
| `GET` | `/api/documents` | 列出所有文档 |
| `GET` | `/api/documents/{id}` | 获取文档详情 |
| `GET` | `/api/documents/{id}/chunks` | 列出文档分块 |
| `DELETE` | `/api/documents/{id}` | 删除文档及其分块 |
| `POST` | `/api/conversations` | 创建会话 |
| `GET` | `/api/conversations` | 列出所有会话 |
| `GET` | `/api/conversations/{id}/messages` | 获取会话历史消息 |
| `DELETE` | `/api/conversations/{id}` | 删除会话 |
| `POST` | `/api/models/select` | 选择默认 LLM 提供商和模型 |
| `GET` | `/api/models` | 获取可用模型信息 |
| `GET` | `/api/health` | 健康检查 |

> 📘 完整交互式 API 文档请访问 `/docs`（Swagger UI）或 `/redoc`。

### 请求 / 响应示例

**聊天（同步）：**
```json
// POST /api/chat
{ "message": "What is React?" }

// 响应
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

**Assistant 流式（SSE）：**
```json
// POST /api/assistant/{conversation_id}/stream
{ "message": "Search docs about React hooks" }

// 事件序列：
// assistant_start → route_decision → tool_call_start → delta* → tool_call_end → done
```

---

## ⚙️ 配置说明

主要环境变量（写入 `.env` 文件）：

```env
# ─── LLM 提供商 ──────────────────────────────
# "ollama" 或 "deepseek"
LLM_PROVIDER=ollama

# ─── Ollama 配置 ─────────────────────────────
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=gemma4:e2b
OLLAMA_TIMEOUT=1200
OLLAMA_KEEP_ALIVE=5m

# ─── DeepSeek 配置 ───────────────────────────
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_API_KEY=your_api_key
DEEPSEEK_MODEL=deepseek-v4-flash
DEEPSEEK_TIMEOUT=120
DEEPSEEK_THINKING_ENABLED=false

# ─── PostgreSQL 配置 ─────────────────────────
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=ai_backend
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password

# ─── 嵌入模型配置 ────────────────────────────
EMBEDDING_MODEL=intfloat/multilingual-e5-base
EMBEDDING_BATCH_SIZE=1500
EMBEDDING_DIMENSION=768

# ─── RAG 配置 ────────────────────────────────
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

# ─── Agent 配置 ──────────────────────────────
AGENT_PLANNER_TYPE=llm
```

---

## 📂 项目结构

```
NexusAI/
├── src/app/
│     ├── api/
│     │     ├── routers/            # FastAPI 路由处理器
│     │     │     ├── agent.py       # Agent 对话 & 追踪端点
│     │     │     ├── assistant.py   # Assistant 流式编排
│     │     │     ├── chat.py        # 聊天（同步 + 流式）
│     │     │     ├── conversations.py # 会话 CRUD
│     │     │     ├── documents.py   # 文档上传/列表/删除
│     │     │     ├── embeddings.py  # 嵌入管理
│     │     │     ├── history_models.py # 历史 & 模型选择
│     │     │     └── base.py        # 基础路由配置
│     │     ├── routes.py           # 路由聚合
│     │     └── exception_handlers.py # 全局异常处理
│     ├── services/
│     │     ├── agent/              # Agent 循环、规划器、Prompt 构建
│     │     │     ├── agent_service.py    # Agent 主服务
│     │     │     ├── loop.py             # ReAct 风格执行循环
│     │     │     ├── planner.py          # 规则驱动规划器
│     │     │     ├── llm_planner.py      # LLM 驱动规划器
│     │     │     ├── planner_parser.py   # JSON Schema 校验
│     │     │     ├── planner_prompt_builder.py # 规划器 Prompt
│     │     │     ├── decision_schema.py    # 工具调用 JSON Schema
│     │     │     └── state.py              # Agent 状态模型
│     │     ├── assistant/          # 编排器、模式路由、运行存储
│     │     │     ├── orchestrator.py       # 统一流式入口
│     │     │     ├── mode_router.py        # 规则 + LLM 路由
│     │     │     ├── llm_router.py         # LLM 模式分类器
│     │     │     ├── llm_route_prompt.py   # 路由 Prompt
│     │     │     ├── run_store.py          # Assistant 运行持久化
│     │     │     └── event.py              # SSE 事件类型定义
│     │     ├── rag/                # 混合检索器、重排器、查询改写
│     │     │     ├── hybrid_retriever.py   # 向量 + BM25 融合
│     │     │     ├── retriever.py          # 标准向量 + 重排
│     │     │     ├── keyword_retriever.py # BM25 关键词检索
│     │     │     ├── rank_fusion.py        # RRF 算法
│     │     │     ├── mmr.py                # 最大边际相关性
│     │     │     ├── reranker.py           # BGE 交叉编码器封装
│     │     │     ├── reranker_provider.py # FlagEmbedding 提供商
│     │     │     ├── query_rewriter.py     # LLM 查询改写
│     │     │     ├── prompt_builder.py     # RAG System Prompt
│     │     │     └── conversation_rag_service.py # 对话式 RAG
│     │     ├── memory/             # 双层记忆系统
│     │     │     ├── short_term_store.py       # 会话状态存储
│     │     │     ├── short_term_schemas.py     # 状态模型
│     │     │     ├── short_term_builder.py     # 上下文构建器
│     │     │     ├── long_term_store.py        # 长期记忆持久化
│     │     │     ├── long_term_schemas.py      # 记忆模型
│     │     │     ├── long_term_retriever.py    # 语义检索
│     │     │     ├── long_term_writer.py       # LLM 提取 + 存储
│     │     │     ├── long_term_ranker.py       # 综合评分
│     │     │     ├── long_term_deduper.py      # 语义去重
│     │     │     └── long_term_policy.py       # 存储策略
│     │     ├── tools/              # Agent 工具注册表及实现
│     │     │     ├── base.py               # 工具抽象基类
│     │     │     ├── registry.py           # 白名单强制校验
│     │     │     ├── list_docs.py          # 列出知识库文档
│     │     │     ├── search_docs.py        # 语义搜索工具
│     │     │     ├── read_doc.py           # 读取完整文档
│     │     │     └── safety.py             # 结果限制
│     │     ├── llm/                # LLM 提供商实现
│     │     │     ├── base.py               # LLMProvider 抽象基类
│     │     │     ├── factory.py            # 提供商选择工厂
│     │     │     ├── ollama_provider.py    # Ollama REST API
│     │     │     └── deepseek_provider.py # OpenAI 兼容 API
│     │     ├── embedding/          # 嵌入服务
│     │     │     └── sentence_transformer_provider.py # SentenceTransformers
│     │     ├── agent_trace_store.py    # Agent 运行/步骤/事件持久化
│     │     ├── conversation_store.py   # 会话/消息持久化
│     │     ├── document_store.py       # 文档/分块持久化
│     │     ├── vector_store.py         # pgvector 操作
│     │     ├── keyword_store.py        # BM25 关键词搜索
│     │     ├── chunk_splitter.py       # Markdown 感知文本切分
│     │     ├── document_loader.py      # 文件类型验证 & 加载
│     │     ├── context_builder.py      # 上下文窗口组装
│     │     ├── summarizer.py           # 会话摘要生成
│     │     ├── chat_service.py         # 聊天业务逻辑
│     │     ├── conversation_service.py # 会话业务逻辑
│     │     ├── document_service.py     # 文档上传 & 处理
│     │     ├── embedding_service.py    # 嵌入批量处理
│     │     ├── health_service.py       # 健康检查逻辑
│     │     ├── history_service.py      # 历史审计日志
│     │     ├── model_service.py        # 模型选择逻辑
│     │     └── rag/                    # （符号链接至 services/rag）
│     ├── schemas/                # Pydantic 请求/响应模型
│     │     ├── schemas.py          # 核心 API 模型
│     │     ├── agent.py            # Agent 专用模型
│     │     └── assistant.py        # Assistant 专用模型
│     ├── config.py               # 统一配置管理（pydantic-settings）
│     ├── db.py                   # 数据库连接助手
│     ├── paths.py                # 路径工具
│     ├── main.py                 # 入口文件（含端口管理）
│     ├── server.py               # FastAPI 应用（CORS & 静态文件）
│     ├── exceptions.py           # 自定义异常类
│     ├── logger.py               # 日志配置
│     ├── prompts.py              # 聊天 System Prompt
│     └── runtime_config.py       # 运行时提供商选择
├── web/                        # React + TypeScript 前端
│     ├── src/
│     │     ├── components/
│     │     │     ├── ChatLayout/          # 主布局（含侧边栏）
│     │     │     ├── ChatView/            # 对话容器
│     │     │     ├── ChatMessageList/     # 消息渲染
│     │     │     ├── ChatInputBar/        # 输入框（含模式选择）
│     │     │     ├── ChatSenderInput/     # 增强发送输入
│     │     │     ├── Sidebar/             # 会话列表侧边栏
│     │     │     ├── WelcomeScreen/       # 欢迎页面
│     │     │     ├── MarkdownContent/     # 渲染后的 Markdown 输出
│     │     │     ├── ToolCallTimeline/    # Agent 工具调用可视化
│     │     │     ├── TraceDrawer/         # Agent 追踪详情面板
│     │     │     └── FeedbackFooter/      # 消息反馈 UI
│     │     ├── contexts/
│     │     │     └── ChatContext.tsx      # 全局聊天状态
│     │     ├── services/                # API 客户端层
│     │     ├── pages/                   # 路由页面
│     │     └── components/              # 可复用 UI 组件
├── sql/                        # 数据库 Schema 与初始化脚本
│     └── init.sql                # 完整 Schema（含索引）
├── tests/                      # Pytest 测试套件
├── scripts/                    # 工具脚本
│     └── debug_chunk_splitter.py # 分块调试
└── docs/                       # 学习笔记与技术文档
```

---

## 🗄️ 数据库 Schema 概览

数据库包含 **11 张表**，按功能分组：

### 文档管理
| 表名 | 用途 |
|------|------|
| `documents` | 源文件元数据（文件名、类型、状态、分块数） |
| `document_chunks` | 文本分块（含向量、标题、全文搜索向量） |

### 会话与消息
| 表名 | 用途 |
|------|------|
| `conversations` | 会话元数据、摘要、模型/提供商信息 |
| `messages` | 单会话消息时间线（用户/助手角色） |
| `chat_history` | 单轮问答审计日志（含延迟追踪） |

### Agent 可观测性
| 表名 | 用途 |
|------|------|
| `agent_runs` | Agent 执行汇总（状态、步数、延迟、最终回答） |
| `agent_steps` | 单步详情（工具名、参数、结果、成功状态） |
| `agent_events` | 细粒度追踪事件，支持 UI 可视化 |

### 记忆系统
| 表名 | 用途 |
|------|------|
| `assistant_runs` | Assistant 编排器调用记录（含模式和追踪） |
| `conversation_states` | 短期会话记忆（目标、事实、约束） |
| `memory_items` | 跨会话长期记忆（含向量和评分） |

### 关键索引
- **HNSW** (`idx_document_chunks_embedding_hnsw`) — 快速向量相似度搜索
- **GIN tsvector** (`idx_document_chunks_search_vector`) — BM25 全文搜索
- **GIN trgm** (`idx_document_chunks_content_trgm`) — 模糊文本匹配
- **复合索引** (`idx_agent_runs_conversation_id_created_at`) — 按会话查询 Agent 运行

---

## 🤝 贡献指南

欢迎贡献代码！请提交 Issue 或 Pull Request。

### 开发规范
- 遵循现有的代码风格和命名约定
- 为新功能添加测试
- API 变更时更新文档
- 确保所有 LLM 提供商在变更后正常工作

---

## 📄 许可证

本项目采用 **MIT 许可证**。
