# AI 开发转型学习计划：审视与增强版

> 基于原《AI 开发转型学习计划》进一步审视、补全和细化。  
> 目标：从“能看懂路线”升级为“可以按阶段执行、复盘、面试表达、形成作品”。

---

# 1. 对原计划的总体判断

原计划的大方向是正确的。

它已经覆盖了 AI 应用转型最关键的主线：

```text
模型调用
  ↓
Embedding
  ↓
RAG
  ↓
Agent
  ↓
MCP
  ↓
前端产品化
  ↓
部署
  ↓
评测
```

这条路线适合有前端、TypeScript、工程化经验的人向 AI 应用开发 / AI Agent 工程师转型。

但是原计划仍然有几个问题：

1. 每周目标是对的，但执行颗粒度还不够细。
2. 缺少第一阶段的环境准备和项目脚手架规范。
3. RAG 部分还缺少真实工程中最容易出问题的细节。
4. Agent 部分还缺少安全边界、状态管理、错误处理。
5. MCP 部分还缺少客户端接入、调试方式和协议边界。
6. 前端控制台部分还缺少具体交互设计和接口契约。
7. 部署部分偏靠后，但 Docker、配置、日志应该更早进入。
8. 评测部分方向正确，但指标还不够工业化。
9. 缺少“作品包装”和“面试话术”的阶段性沉淀。
10. 缺少风险控制：每阶段可能卡在哪里、如何降级完成。

所以增强版建议从原来的 8 周，调整为：

```text
10 周主线 + 2 周进阶缓冲
```

---

# 2. 转型目标重新定义

不要把目标定义成“学习大模型”。

更准确的目标应该是：

## 成为 AI 应用工程师 / AI Agent 工程师

你需要具备以下能力：

```text
能接模型
能做 RAG
能做 Agent
能接工具
能暴露 MCP 服务
能做前端产品化
能部署
能评测
能讲清楚架构
```

不是算法研究员路线：

```text
训练大模型
研究模型结构
写论文
做分布式训练
改 CUDA Kernel
```

而是工程落地路线：

```text
把模型能力变成企业可用系统
```

---

# 3. 最终项目建议

项目名称：

```text
ai-enterprise-agent
```

项目定位：

```text
面向企业研发规范的 AI Agent 系统。
```

核心场景：

```text
上传企业规范文档
  ↓
系统自动向量化
  ↓
用户提问
  ↓
RAG 检索相关规范
  ↓
Agent 判断是否需要工具
  ↓
模型生成答案或代码
  ↓
返回引用来源和执行轨迹
```

最终你可以把它包装成：

```text
企业代码规范助手
企业知识库问答系统
AI Agent 控制台
MCP 工具服务平台
```

这几个说法都成立。

---

# 4. 增强后的最终目录结构

建议最终结构如下：

```text
ai-enterprise-agent/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   │   ├── chat.py
│   │   │   ├── documents.py
│   │   │   ├── rag.py
│   │   │   ├── agent.py
│   │   │   └── settings.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── logger.py
│   │   │   ├── exceptions.py
│   │   │   └── security.py
│   │   ├── db/
│   │   │   ├── session.py
│   │   │   ├── models.py
│   │   │   └── migrations/
│   │   ├── schemas/
│   │   │   ├── chat.py
│   │   │   ├── document.py
│   │   │   ├── rag.py
│   │   │   └── agent.py
│   │   ├── services/
│   │   │   ├── llm/
│   │   │   │   ├── base.py
│   │   │   │   ├── ollama_provider.py
│   │   │   │   ├── openai_provider.py
│   │   │   │   └── vllm_provider.py
│   │   │   ├── embedding/
│   │   │   │   ├── base.py
│   │   │   │   └── sentence_transformer_provider.py
│   │   │   ├── document/
│   │   │   │   ├── loader.py
│   │   │   │   ├── splitter.py
│   │   │   │   └── parser.py
│   │   │   ├── rag/
│   │   │   │   ├── retriever.py
│   │   │   │   ├── prompt_builder.py
│   │   │   │   └── pipeline.py
│   │   │   ├── agent/
│   │   │   │   ├── loop.py
│   │   │   │   ├── state.py
│   │   │   │   └── planner.py
│   │   │   └── tools/
│   │   │       ├── base.py
│   │   │       ├── search_docs.py
│   │   │       ├── read_doc.py
│   │   │       └── list_docs.py
│   │   └── utils/
│   ├── scripts/
│   │   ├── init_db.py
│   │   ├── ingest_docs.py
│   │   └── eval_rag.py
│   ├── tests/
│   ├── pyproject.toml
│   └── README.md
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Documents/
│   │   │   ├── KnowledgeChat/
│   │   │   ├── AgentChat/
│   │   │   ├── ToolLogs/
│   │   │   └── Settings/
│   │   ├── services/
│   │   ├── components/
│   │   ├── stores/
│   │   └── types/
│   ├── package.json
│   └── README.md
│
├── mcp-server/
│   ├── src/
│   │   ├── main.ts
│   │   ├── tools/
│   │   ├── resources/
│   │   ├── clients/
│   │   └── schemas/
│   ├── package.json
│   └── README.md
│
├── docs/
│   ├── frontend-style-guide.md
│   ├── api-style-guide.md
│   ├── project-structure.md
│   ├── prompt-style-guide.md
│   ├── architecture.md
│   └── dev-log.md
│
├── eval/
│   ├── cases.json
│   ├── report.md
│   └── run_eval.py
│
├── docker-compose.yml
├── .env.example
└── README.md
```

---

# 5. 10 周增强版计划

---

## 第 0 周：环境准备与项目骨架

原计划缺少这一周，但实际很重要。

### 阶段目标

把开发环境、目录结构、基础规范全部准备好。

### 要完成的事情

#### 1. 创建仓库

```bash
mkdir ai-enterprise-agent
cd ai-enterprise-agent
git init
```

#### 2. 创建基础目录

```text
backend/
frontend/
mcp-server/
docs/
eval/
```

#### 3. 准备 Python 环境

推荐使用：

```bash
python -m venv .venv
source .venv/bin/activate
```

或者使用 `uv` 管理也可以，但初学阶段先用 venv 更直观。

#### 4. 准备 Node 环境

```bash
node -v
pnpm -v
```

建议：

```text
Node.js 22+
pnpm
```

#### 5. 准备基础配置

创建：

```text
.env.example
.gitignore
README.md
docs/dev-log.md
```

`.env.example` 示例：

```env
APP_ENV=development
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ai_agent
OLLAMA_BASE_URL=http://127.0.0.1:11434
DEFAULT_LLM_PROVIDER=ollama
DEFAULT_LLM_MODEL=qwen2.5:7b
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

### 本周产物

- Git 仓库
- 基础目录
- Python 虚拟环境
- Node 环境
- `.env.example`
- 第一版 README
- 开发日志文件

### 验收标准

你能执行：

```bash
tree -L 2
```

看到清晰项目结构。

---

## 第 1 周：FastAPI + 模型调用服务

### 阶段目标

做出最小模型服务。

```text
用户请求
  ↓
FastAPI
  ↓
LLMProvider
  ↓
Ollama
  ↓
返回回答
```

### 要学什么

- FastAPI 路由
- Pydantic 请求 / 响应模型
- async / await
- httpx
- Provider 抽象
- Ollama HTTP API
- 错误处理

### 具体任务

#### 任务 1：创建 FastAPI 项目

```text
backend/app/main.py
backend/app/api/chat.py
backend/app/schemas/chat.py
backend/app/services/llm/base.py
backend/app/services/llm/ollama_provider.py
```

#### 任务 2：定义请求响应模型

```python
from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str
    model: str | None = None

class ChatResponse(BaseModel):
    answer: str
    provider: str
    model: str
```

#### 任务 3：定义 Provider 抽象

```python
from abc import ABC, abstractmethod

class LLMProvider(ABC):
    @abstractmethod
    async def chat(self, messages: list[dict]) -> str:
        pass
```

#### 任务 4：实现 OllamaProvider

通过 HTTP 调用：

```text
POST /api/chat
```

#### 任务 5：实现接口

```http
POST /chat
```

### 增强要求

不要只返回 answer，建议返回：

```json
{
  "answer": "...",
  "provider": "ollama",
  "model": "qwen2.5:7b",
  "usage": {
    "prompt_tokens": 0,
    "completion_tokens": 0
  },
  "latency_ms": 1200
}
```

即使 Ollama 不一定直接给出完整 token usage，也要先预留结构。

### 常见卡点

| 卡点 | 解决方式 |
|---|---|
| Ollama 端口访问失败 | 检查 `ollama serve` 和 11434 监听 |
| FastAPI import 报错 | 使用 `python -m uvicorn app.main:app --reload` |
| async 不理解 | 先把它理解成“等待外部 IO 不阻塞服务” |
| Provider 觉得多余 | 后面要支持多个模型，不抽象会重构痛苦 |

### 本周产物

- `/chat`
- `OllamaProvider`
- 基础错误处理
- 请求耗时统计

### 验收标准

```bash
curl -X POST http://127.0.0.1:8000/chat   -H "Content-Type: application/json"   -d '{"message":"什么是 RAG？"}'
```

可以返回结构化结果。

---

## 第 2 周：Streaming + 配置系统 + 日志系统

原计划把 streaming 放到第 7 周，但建议提前做。因为 AI 产品对流式输出依赖很强。

### 阶段目标

让模型服务更像真实 AI 应用。

```text
配置可变
日志可查
支持流式输出
错误可定位
```

### 要学什么

- Server-Sent Events
- Streaming Response
- pydantic-settings
- logging
- 统一异常处理

### 具体任务

#### 任务 1：配置系统

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    ollama_base_url: str = "http://127.0.0.1:11434"
    default_llm_model: str = "qwen2.5:7b"

    class Config:
        env_file = ".env"
```

#### 任务 2：日志系统

记录：

```text
请求时间
模型名称
Provider
耗时
错误信息
```

#### 任务 3：流式接口

```http
POST /chat/stream
```

返回 SSE：

```text
data: {"delta":"你好"}
data: {"delta":"，"}
data: {"delta":"我是"}
data: [DONE]
```

#### 任务 4：统一错误返回

示例：

```json
{
  "error": {
    "code": "LLM_PROVIDER_ERROR",
    "message": "Ollama service unavailable"
  }
}
```

### 本周产物

- `.env` 配置
- 日志模块
- `/chat/stream`
- 统一错误结构

### 验收标准

前端或 curl 可以看到流式输出。

---

## 第 3 周：文档上传 + Chunk 切分

### 阶段目标

开始建设知识库。

```text
上传文档
  ↓
解析文本
  ↓
切分 chunk
  ↓
保存 document 和 chunk
```

### 要学什么

- 文件上传
- 文本解析
- chunk size
- chunk overlap
- Markdown 结构
- 文档元数据

### 具体任务

#### 任务 1：文档上传接口

```http
POST /documents/upload
```

支持：

```text
.md
.txt
```

暂时不要做 PDF。

#### 任务 2：设计数据库

建议比原计划多加字段。

```sql
CREATE TABLE documents (
  id UUID PRIMARY KEY,
  filename TEXT NOT NULL,
  file_type TEXT NOT NULL,
  content TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'pending',
  error_message TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE document_chunks (
  id UUID PRIMARY KEY,
  document_id UUID REFERENCES documents(id),
  chunk_index INT NOT NULL,
  content TEXT NOT NULL,
  token_count INT,
  char_count INT,
  heading TEXT,
  metadata JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);
```

#### 任务 3：Chunk 切分策略

第一版建议：

```text
优先按 Markdown 标题切
再按段落切
最后按字符长度兜底
```

不要一开始只按固定字符数切，否则文档结构会被破坏。

#### 任务 4：文档状态机

```text
pending
processing
completed
failed
```

### 本周产物

- `/documents/upload`
- `/documents`
- `/documents/{id}`
- `/documents/{id}/chunks`
- 文档状态字段
- chunk 切分函数

### 验收标准

上传一个 Markdown 后，可以看到：

```text
文档记录
多个 chunk
每个 chunk 有 heading / metadata
```

---

## 第 4 周：Embedding + pgvector

### 阶段目标

把 chunk 变成可检索的语义向量。

```text
chunk
  ↓
embedding model
  ↓
vector
  ↓
pgvector
```

### 要学什么

- embedding model
- sentence-transformers
- vector dimension
- pgvector
- cosine distance
- index
- batch embedding

### 具体任务

#### 任务 1：安装 pgvector

使用 docker-compose：

```yaml
services:
  postgres:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: ai_agent
    ports:
      - "5432:5432"
```

#### 任务 2：新增 embedding 字段

```sql
CREATE EXTENSION IF NOT EXISTS vector;

ALTER TABLE document_chunks
ADD COLUMN embedding VECTOR(384);

ALTER TABLE document_chunks
ADD COLUMN embedding_model TEXT;
```

注意：

```text
VECTOR(384)
```

要和你选择的 embedding 模型维度一致。

例如：

```text
all-MiniLM-L6-v2 通常是 384 维
bge-m3 通常是 1024 维
```

#### 任务 3：EmbeddingProvider 抽象

```python
class EmbeddingProvider:
    async def embed_text(self, text: str) -> list[float]:
        pass

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        pass
```

#### 任务 4：批量向量化

不要一个 chunk 调一次模型。

应该：

```text
一次处理多个 chunk
批量生成 embedding
批量写入数据库
```

### 本周产物

- pgvector 数据库
- EmbeddingProvider
- chunk embedding 入库
- 批量处理脚本

### 验收标准

数据库中每个 chunk 都有 embedding。

---

## 第 5 周：RAG 检索 + 问答

### 阶段目标

做出可用 RAG。

```text
问题
  ↓
问题 embedding
  ↓
向量检索 top_k
  ↓
构造 context
  ↓
模型回答
  ↓
返回 sources
```

### 要学什么

- similarity search
- top_k
- score threshold
- prompt template
- citation
- context packing
- no answer policy

### 具体任务

#### 任务 1：检索 SQL

示例：

```sql
SELECT
  id,
  content,
  metadata,
  1 - (embedding <=> :query_embedding) AS score
FROM document_chunks
ORDER BY embedding <=> :query_embedding
LIMIT :top_k;
```

#### 任务 2：RAG Search 接口

```http
POST /rag/search
```

返回：

```json
{
  "query": "组件如何命名？",
  "chunks": [
    {
      "chunk_id": "xxx",
      "content": "...",
      "score": 0.82,
      "filename": "frontend-style-guide.md",
      "heading": "组件命名"
    }
  ]
}
```

#### 任务 3：RAG Ask 接口

```http
POST /ask
```

返回：

```json
{
  "answer": "...",
  "sources": [
    {
      "filename": "frontend-style-guide.md",
      "heading": "组件命名",
      "score": 0.82,
      "content": "..."
    }
  ],
  "trace": {
    "top_k": 5,
    "score_threshold": 0.55,
    "model": "qwen2.5:7b"
  }
}
```

#### 任务 4：Prompt 模板

```text
你是一个企业研发规范助手。

你必须只根据【资料】回答问题。
如果资料中没有明确答案，请回答：根据当前知识库资料，无法确定。
回答时尽量指出依据来自哪份文档。

【资料】
{context}

【问题】
{question}
```

### 本周产物

- `/rag/search`
- `/ask`
- RAG Pipeline
- sources
- trace

### 验收标准

1. 有资料时，能基于资料回答。
2. 无资料时，能拒答。
3. 返回 sources。
4. 返回 score。
5. 能看到 trace。

---

## 第 6 周：RAG 优化 + Rerank + 评测雏形

原计划把评测放最后，但建议从 RAG 阶段就开始做最小评测。

### 阶段目标

不要停留在“感觉能用”，要开始量化。

### 要学什么

- recall
- precision
- rerank
- hit rate
- citation rate
- regression test

### 具体任务

#### 任务 1：建立第一版 eval cases

```json
[
  {
    "id": "case_001",
    "question": "React 组件应该如何命名？",
    "expected_keywords": ["PascalCase"],
    "expected_source": "frontend-style-guide.md",
    "must_cite": true
  }
]
```

#### 任务 2：编写 eval 脚本

统计：

```text
关键词命中率
是否有引用
是否召回正确文档
平均耗时
```

#### 任务 3：增加 Rerank 预留接口

先不一定接真实 reranker，但代码结构预留：

```python
class Reranker:
    async def rerank(self, query: str, chunks: list[Chunk]) -> list[Chunk]:
        return chunks
```

#### 任务 4：对比不同参数

比较：

```text
top_k=3
top_k=5
top_k=10
score_threshold=0.4
score_threshold=0.6
score_threshold=0.8
```

### 本周产物

- `eval/cases.json`
- `eval/run_eval.py`
- 第一版评测报告
- Rerank 抽象

### 验收标准

你能明确说出：

```text
top_k=5 时效果比 top_k=3 更稳定
score_threshold 太高会导致拒答变多
```

---

## 第 7 周：Agent Loop + Tool Calling

### 阶段目标

让系统具备工具调用能力。

### 要学什么

- tool schema
- function calling
- agent loop
- max steps
- tool result
- execution trace
- permission boundary

### 具体任务

#### 任务 1：工具基础协议

```python
class Tool:
    name: str
    description: str

    async def run(self, arguments: dict) -> dict:
        pass
```

#### 任务 2：实现三个工具

```text
search_docs
read_doc
list_docs
```

#### 任务 3：Agent 状态

```json
{
  "messages": [],
  "steps": [],
  "max_steps": 3,
  "status": "running"
}
```

#### 任务 4：Agent Trace

每次工具调用都记录：

```json
{
  "tool_name": "search_docs",
  "arguments": {
    "query": "React 组件命名"
  },
  "result": {},
  "latency_ms": 200,
  "success": true
}
```

#### 任务 5：终止条件

必须有：

```text
最多调用 3 次工具
工具失败后可重试 1 次
模型给出 final answer 后停止
```

### 本周产物

- `/agent/chat`
- `agent/loop.py`
- `tools/`
- agent trace
- max step 限制

### 验收标准

用户问：

```text
根据规范帮我生成一个 Button 组件模板
```

系统能：

```text
搜索规范
读取相关 chunk
生成代码
返回工具调用过程
```

---

## 第 8 周：MCP Server

### 阶段目标

把企业规范能力暴露给外部 AI 工具。

### 要学什么

- MCP Server
- Tools
- Resources
- Zod Schema
- stdio / HTTP
- MCP Inspector
- 客户端配置

### 具体任务

#### 任务 1：创建 Node MCP 项目

```text
mcp-server/
├── src/
│   ├── main.ts
│   ├── tools/
│   ├── clients/
│   └── schemas/
```

#### 任务 2：封装 Backend Client

```ts
class BackendClient {
  async searchDocs(query: string) {}
  async listDocs() {}
}
```

#### 任务 3：实现 MCP Tools

```text
search_frontend_standards
get_component_rules
generate_component_template
```

#### 任务 4：调试工具

使用 MCP Inspector 或 AI 客户端配置验证。

#### 任务 5：写清楚边界

MCP Server 不直接操作数据库。

推荐架构：

```text
AI Client
  ↓
MCP Server
  ↓
Backend API
  ↓
RAG / Agent / DB
```

### 本周产物

- 可运行 MCP Server
- 3 个工具
- MCP 调试文档
- 客户端配置示例

### 验收标准

外部 AI 工具可以调用你的 MCP 工具拿到规范内容。

---

## 第 9 周：前端控制台

### 阶段目标

把系统做成一个能展示的产品。

### 要学什么

你已经会前端，所以重点不是技术，而是 AI 产品交互。

### 页面 1：文档库

字段：

```text
文件名
文件类型
状态
chunk 数量
embedding 状态
创建时间
操作
```

操作：

```text
上传
删除
重新向量化
查看 chunk
```

### 页面 2：知识库问答

必须展示：

```text
问题
回答
引用来源
召回 chunk
score
耗时
模型名称
```

### 页面 3：Agent 对话

必须展示：

```text
用户消息
模型思考结果的可解释摘要
工具调用名称
工具入参
工具结果
最终答案
```

注意：

```text
不要展示模型内部隐私链路或不可控推理，只展示可解释的执行步骤。
```

### 页面 4：工具日志

字段：

```text
时间
工具名
参数
结果
耗时
状态
```

### 页面 5：设置页

配置：

```text
LLM Provider
LLM Model
Embedding Model
top_k
score_threshold
max_agent_steps
```

### 本周产物

- 可演示 Web 控制台
- 支持流式回答
- 支持引用来源
- 支持工具调用日志

### 验收标准

一个面试官打开页面后，5 分钟内能理解你项目的价值。

---

## 第 10 周：部署、README、面试包装

### 阶段目标

把项目从“能跑”变成“能展示”。

### 要学什么

- Docker Compose
- README 结构
- 架构图
- demo 数据
- 面试表达
- 评测报告

### 具体任务

#### 任务 1：docker-compose

包含：

```text
postgres + pgvector
backend
frontend
mcp-server
```

Ollama 可以先作为外部依赖，不强行放入 compose。

#### 任务 2：准备 demo 文档

```text
frontend-style-guide.md
api-style-guide.md
project-structure.md
```

#### 任务 3：完善 README

README 必须包含：

```text
项目背景
解决问题
技术栈
架构图
核心流程
本地启动
接口说明
MCP 工具说明
评测结果
后续规划
```

#### 任务 4：准备面试讲解稿

控制在：

```text
1 分钟版本
3 分钟版本
5 分钟版本
```

### 本周产物

- docker-compose.yml
- 完整 README
- architecture.md
- eval/report.md
- demo docs
- 面试讲解稿

### 验收标准

你可以把项目发给别人，对方按 README 能跑起来。

---

# 6. 原计划最需要补的 8 个点

## 6.1 环境准备必须前置

原计划从第 1 周直接做模型调用，但真实开发会先卡在：

```text
Python 环境
项目结构
.env
数据库
Ollama
依赖管理
```

所以必须增加第 0 周。

---

## 6.2 Streaming 应该提前

AI 产品如果没有流式输出，体验会很差。

所以建议第 2 周就做：

```text
/chat/stream
```

而不是等到模型部署阶段。

---

## 6.3 文档切分不能只按字符数

真实 RAG 中，chunk 质量直接决定答案质量。

建议切分优先级：

```text
Markdown 标题
段落
列表
代码块
固定长度兜底
```

不要粗暴每 500 字切一次。

---

## 6.4 数据库字段要考虑状态

文档处理不是瞬间完成的。

必须有：

```text
pending
processing
completed
failed
```

否则前端无法展示处理状态，失败也不好排查。

---

## 6.5 Embedding 维度要和模型绑定

原计划写了 `VECTOR(768)`，但这取决于模型。

例如：

```text
all-MiniLM-L6-v2: 384 维
bge-m3: 1024 维
```

所以数据库设计要明确：

```text
embedding_model
embedding_dimension
```

---

## 6.6 Agent 必须有执行边界

Agent 不是越自由越好。

必须限制：

```text
max_steps
allowed_tools
tool timeout
retry count
permission boundary
```

否则它会失控、循环调用、乱调工具。

---

## 6.7 MCP 要明确边界

MCP Server 不建议直接混进业务后端。

推荐：

```text
MCP Server 是工具适配层
Backend 是业务能力层
DB 是数据层
```

这样结构清楚，也更好讲。

---

## 6.8 Eval 应该从 RAG 阶段开始

不要等项目最后才评测。

RAG 一做完就要开始建立小型测试集。

否则你后面无法判断：

```text
chunk 策略是否变好
top_k 是否合适
prompt 是否稳定
rerank 是否有效
```

---

# 7. 每周执行清单

## 每周固定检查

每周结束必须回答：

```text
1. 本周跑通了哪个接口？
2. 本周新增了哪些文件？
3. 本周遇到的最大问题是什么？
4. 有没有写 dev-log？
5. 有没有更新 README？
6. 有没有可演示功能？
7. 有没有可面试讲点？
```

---

## 每日固定节奏

推荐：

```text
20 分钟：复习昨天代码
40 分钟：学一个必要概念
90 分钟：写代码
30 分钟：调试和记录
20 分钟：更新 dev-log
```

最少也要保证：

```text
每天一次 commit
每天一条 dev-log
每两天一个可运行小功能
```

---

# 8. 每阶段风险和降级方案

## 第 1-2 周风险

### 风险

```text
Python 工程不熟
FastAPI import 报错
Ollama 调不通
streaming 不理解
```

### 降级方案

先只做同步 `/chat`。

流式输出可以晚 2 天补。

---

## 第 3-4 周风险

### 风险

```text
PostgreSQL / pgvector 配置卡住
embedding 模型下载慢
数据库维度不匹配
```

### 降级方案

先用内存列表或 SQLite 存 chunk。

pgvector 卡住时不要停太久，先跑通流程。

---

## 第 5-6 周风险

### 风险

```text
RAG 召回效果差
回答引用不稳定
模型胡编
```

### 降级方案

先降低目标：

```text
只要求召回正确 chunk
再要求回答正确
最后要求引用稳定
```

---

## 第 7 周风险

### 风险

```text
Agent tool calling 格式不稳定
模型不按 JSON 输出
循环调用工具
```

### 降级方案

第一版可以不用模型自动决定工具。

先写规则版：

```text
只要问题包含“规范 / 文档 / 根据”，就调用 search_docs
```

然后再升级为模型 tool calling。

---

## 第 8 周风险

### 风险

```text
MCP 配置复杂
客户端识别不到工具
stdio / HTTP 搞混
```

### 降级方案

先完成 MCP Server 自测。

外部客户端接入可以作为增强项。

---

## 第 9-10 周风险

### 风险

```text
前端做太复杂
部署卡住
README 没时间写
```

### 降级方案

前端优先做 3 个页面：

```text
文档库
知识库问答
Agent 对话
```

其他页面可以后补。

---

# 9. 面试竞争力排序

完成后，面试时优先讲这些：

## 第一优先级：完整链路

```text
我从文档上传、chunk、embedding、向量检索、prompt 构造、模型回答、引用来源、前端展示做了完整链路。
```

## 第二优先级：Agent 工具调用

```text
我实现了一个简单 Agent Loop，支持工具调用、执行 trace、最大步数限制和工具结果回填。
```

## 第三优先级：MCP

```text
我把企业规范检索能力封装成 MCP Server，让外部 AI 工具可以复用。
```

## 第四优先级：评测

```text
我不是靠感觉判断效果，而是写了 eval cases，统计关键词命中率、引用率、召回正确率和响应耗时。
```

## 第五优先级：前端产品化

```text
我做了控制台，可以展示文档状态、RAG 引用、Agent 工具调用过程和系统配置。
```

---

# 10. 最终你应该能讲清楚的问题

## 模型相关

```text
什么是 token？
什么是 embedding？
为什么 embedding 可以做语义检索？
chat model 和 embedding model 有什么区别？
Ollama 和 vLLM 有什么区别？
为什么要做 Provider 抽象？
```

## RAG 相关

```text
为什么要 chunk？
chunk size 怎么定？
top_k 怎么定？
score threshold 有什么用？
RAG 为什么能降低幻觉？
RAG 为什么不能完全消除幻觉？
如何判断 RAG 效果？
```

## Agent 相关

```text
Agent 和普通 Chat 有什么区别？
工具调用为什么需要 schema？
Agent Loop 如何停止？
工具调用失败怎么办？
如何防止 Agent 乱调工具？
```

## MCP 相关

```text
MCP 和 Function Calling 有什么区别？
MCP Server 解决什么问题？
MCP Tool / Resource / Prompt 分别是什么？
MCP Server 为什么适合企业工具集成？
```

## 工程相关

```text
为什么要分 backend / frontend / mcp-server？
为什么 MCP Server 不直接连数据库？
为什么要有 eval？
为什么要展示 trace？
如何部署？
如何排查问题？
```

---

# 11. 最小可交付版本

如果时间不够，最低限度做这个版本：

```text
backend:
  /chat
  /documents/upload
  /rag/search
  /ask
  /agent/chat

frontend:
  文档上传
  RAG 问答
  Agent 对话

mcp-server:
  search_frontend_standards

eval:
  10 条测试 case
  简单评测报告
```

这个版本已经足够作为转型作品。

---

# 12. 不建议现在投入太多的内容

暂时不要重投入：

```text
从零训练大模型
复杂微调
GraphRAG
多 Agent 协作
复杂权限系统
PDF 高精度解析
私有化大规模部署
CUDA 优化
分布式推理
```

这些都可以后续做。

当前最高 ROI 是：

```text
RAG + Agent + MCP + 前端产品化 + Eval
```

---

# 13. 结论

原计划方向正确，但更像路线图。

增强后应该变成：

```text
第 0 周：环境与项目骨架
第 1 周：FastAPI + Ollama
第 2 周：Streaming + 配置 + 日志
第 3 周：文档上传 + Chunk
第 4 周：Embedding + pgvector
第 5 周：RAG 问答
第 6 周：RAG 优化 + Eval 雏形
第 7 周：Agent Loop
第 8 周：MCP Server
第 9 周：前端控制台
第 10 周：部署 + README + 面试包装
```

这版会更适合真正执行，也更适合最终面向转型。

最终你要交付的不是“学习记录”，而是：

```text
一个能跑的 AI 工程项目
一套能解释的架构
一份能展示的 README
一套能证明效果的评测报告
一段能讲清楚的面试表达
```
