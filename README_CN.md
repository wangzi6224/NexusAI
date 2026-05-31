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
<img src="https://img.shields.io/badge/向量嵌入-多语言-red?style=flat-square" alt="Embedding">

<br/><br/>

**生产就绪的全栈 AI 应用平台 —— 混合 RAG、工具 Agent、多 LLM 灵活切换。**

[English README](./README.md) · [快速开始](#-快速开始) · [API 参考](#-api-参考) · [架构说明](#-系统架构)

</div>

---

## 📖 项目简介

**NexusAI** 是一个全栈 AI 应用平台，集成高性能 FastAPI 后端与现代 React 前端。平台以**检索增强生成（RAG）**、**工具调用 Agent** 和**多 LLM 提供商**为核心，提供智能、流畅的对话体验。

### ✨ 核心特性

| 功能 | 说明 |
|---|---|
| 🤖 **多 LLM 路由** | 通过配置在本地 Ollama 模型与 DeepSeek 云端 API 之间无缝切换 |
| 📚 **混合 RAG** | 向量检索 + BM25 关键词检索，RRF 融合排序，BGE 重排器精选结果 |
| 🛠️ **工具增强 Agent** | 多步推理循环，内置 `list_docs`、`search_docs`、`read_doc` 三类工具 |
| 💬 **多轮对话** | 持久化会话历史，支持上下文摘要压缩 |
| 📄 **文档管理** | 上传、切片、向量化并索引 Markdown 与纯文本文档 |
| 🔄 **流式输出** | 基于 Server-Sent Events（SSE）的逐 token 实时流式输出 |
| 🔍 **Agent 追踪** | 完整可观测的 Agent 推理步骤和工具调用日志 |
| 🎛️ **智能模式路由** | 根据查询意图自动分发至 `chat`、`rag` 或 `agent` 模式 |

---

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                        NexusAI 平台                             │
├─────────────────┬───────────────────────────────────────────────┤
│   前端层        │  React 18 + TypeScript + Ant Design X         │
│   (web/)        │  Tailwind CSS · SSE 流式 · Trace 抽屉         │
├─────────────────┼───────────────────────────────────────────────┤
│   API 层        │  FastAPI · 路由: chat / rag / agent /          │
│   (src/app/api) │  assistant / conversations / documents         │
├─────────────────┼───────────────────────────────────────────────┤
│                 │  ┌──────────┐  ┌──────────┐  ┌────────────┐  │
│   服务层        │  │  Agent   │  │   RAG    │  │ Assistant  │  │
│                 │  │  循环    │  │ 混合检索 │  │ 编排器     │  │
│                 │  │  规划器  │  │ 重排器   │  │ 模式路由   │  │
│                 │  └────┬─────┘  └────┬─────┘  └─────┬──────┘  │
│                 │       │             │               │          │
│                 │  ┌────▼─────────────▼───────────────▼──────┐  │
│                 │  │              LLM 工厂                    │  │
│                 │  │    OllamaProvider  │  DeepSeekProvider   │  │
│                 │  └──────────────────────────────────────────┘  │
├─────────────────┼───────────────────────────────────────────────┤
│   数据层        │  PostgreSQL + pgvector · E5-base 嵌入模型     │
│                 │  BGE 重排器 · 文档切片器 · 文档加载器         │
└─────────────────┴───────────────────────────────────────────────┘
```

---

## 🔬 核心模块详解

### 🧠 RAG 管道

NexusAI 实现了**三阶段混合 RAG** 管道：

1. **查询改写** — 对用户问题进行语义扩展，提升召回覆盖率
2. **混合检索** — 稠密向量检索（pgvector）与稀疏 BM25 关键词检索并行执行，使用**互惠排名融合（RRF）**合并结果
3. **重排序** — 使用 `BAAI/bge-reranker-base` 交叉编码器对候选结果精排，再交给 LLM 生成最终回答

```
用户问题
    │
    ▼
查询改写器 ──► 向量检索（pgvector，top-30）
                    +
              关键词检索（BM25，top-30）
                    │
               RRF 融合（top-20）
                    │
              BGE 重排器（top-5）
                    │
              LLM 生成回答
```

### 🛠️ Agent 推理循环

Agent 采用 **ReAct 风格**的步骤循环，支持可配置的最大步数限制：

```
用户问题
    │
    ▼
规划器（LLM） ──► 工具选择 ──► 工具执行 ──► 观察结果
    ▲                                          │
    └──────────────────────────────────────────┘
    （循环直到 DONE 或达到最大步数）
    │
    ▼
最终回答
```

**内置工具列表：**

| 工具名 | 说明 |
|--------|------|
| `list_docs` | 列出知识库中的所有文档 |
| `search_docs` | 在知识库中执行语义搜索 |
| `read_doc` | 读取指定文档的完整内容 |

### 🔄 Assistant 编排器

`AssistantOrchestrator` 是统一的流式入口，通过 `ModeRouter` 进行请求路由：

| 模式 | 行为 |
|------|------|
| `chat` | 直接多轮 LLM 对话 |
| `agent` | 工具增强推理，可访问知识库 |
| `auto` | 基于规则分析查询意图，自动路由至 `chat` 或 `agent` |

---

## 🛠️ 技术栈

### 后端

| 分类 | 技术 |
|------|------|
| 运行时 | Python 3.11+ · FastAPI · Uvicorn |
| LLM 提供商 | Ollama（本地）· DeepSeek API（云端）|
| 向量嵌入 | `intfloat/multilingual-e5-base`（768 维，多语言）|
| 重排器 | `BAAI/bge-reranker-base`（交叉编码器）|
| 数据库 | PostgreSQL 15+ + `pgvector` 扩展 |
| 配置管理 | Pydantic Settings + `.env` 文件 |
| 测试框架 | Pytest |

### 前端

| 分类 | 技术 |
|------|------|
| 框架 | React 18 + TypeScript |
| UI 组件库 | Ant Design X（AI 原生组件）|
| 样式 | Tailwind CSS |
| 构建工具 | Vite / pnpm |

---

## 🚀 快速开始

### 环境要求

- Python 3.11 – 3.12
- PostgreSQL 15+（含 pgvector 扩展）
- [Ollama](https://ollama.com)（本地 LLM）
- Node.js 18+ 与 pnpm（前端）

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

### 第三步：拉取本地模型（Ollama）

```bash
ollama serve
ollama pull gemma4:e2b   # 或其他支持的模型
```

### 第四步：启动后端服务

```bash
uv run -m src.app.main --reload
# API 服务：http://localhost:8000
# Swagger 文档：http://localhost:8000/docs
```

### 第五步：启动前端

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
| `POST` | `/api/chat` | 同步聊天 |
| `POST` | `/api/chat/stream` | 流式聊天（SSE）|
| `POST` | `/api/assistant/{id}/stream` | Assistant 流式接口（自动模式路由）|
| `POST` | `/api/rag/ask` | 单轮 RAG 问答 |
| `GET` | `/api/rag/search` | 检索相关文档片段 |
| `POST` | `/api/agent/chat` | Agent 多步推理对话 |
| `GET` | `/api/agent/runs/{run_id}` | Agent 追踪详情 |
| `POST` | `/api/documents/upload` | 上传文档 |
| `GET` | `/api/documents` | 列出所有文档 |
| `POST` | `/api/conversations` | 创建会话 |
| `GET` | `/api/conversations/{id}/messages` | 获取会话历史消息 |
| `GET` | `/api/health` | 健康检查 |

> 📘 完整交互式 API 文档请访问 `/docs`（Swagger UI）或 `/redoc`。

---

## ⚙️ 配置说明

主要环境变量（写入 `.env` 文件）：

```env
# LLM 提供商：选择 "ollama" 或 "deepseek"
LLM_PROVIDER=ollama

# Ollama 配置
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=gemma4:e2b
OLLAMA_KEEP_ALIVE=5m

# DeepSeek 配置
DEEPSEEK_API_KEY=your_api_key
DEEPSEEK_MODEL=deepseek-v4-flash

# PostgreSQL 配置
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=ai_backend
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password

# RAG 配置
RERANKER_ENABLED=true
EMBEDDING_MODEL=intfloat/multilingual-e5-base
EMBEDDING_DIMENSION=768
RAG_CANDIDATE_K=30
```

---

## 📂 项目结构

```
NexusAI/
├── src/app/
│   ├── api/
│   │   └── routers/          # FastAPI 路由处理器
│   ├── services/
│   │   ├── agent/            # Agent 循环、规划器、Prompt 构建
│   │   ├── rag/              # 混合检索器、重排器、查询改写
│   │   ├── assistant/        # 编排器、模式路由、运行记录
│   │   ├── llm/              # Ollama 与 DeepSeek 提供商实现
│   │   ├── embedding/        # Sentence-Transformer 嵌入服务
│   │   └── tools/            # Agent 工具注册表及工具实现
│   ├── schemas/              # Pydantic 请求/响应模型
│   └── config.py             # 统一配置管理（pydantic-settings）
├── web/                      # React + TypeScript 前端
├── sql/                      # 数据库 Schema 与初始化脚本
├── tests/                    # Pytest 测试套件
└── docs/                     # 学习笔记与技术文档
```

---

## 🤝 参与贡献

欢迎提交 Issue 或 Pull Request！

---

## 📄 许可证

本项目基于 **MIT 许可证** 开源。

---

<div align="center">

📖 **[View English README →](./README.md)**

*使用 FastAPI · Ollama · pgvector · React 构建，致力于打造生产就绪的 AI 应用基础设施*

</div>
