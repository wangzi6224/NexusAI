# AI 开发转型学习计划：最强实战版（基于当前第 2 周进度）

> 适用对象：已有前端工程经验，正在向 AI 应用工程师 / AI Agent 工程师转型。  
> 当前状态：已完成第 1-2 周，即 FastAPI + Ollama 基础调用、Streaming、配置、日志、异常处理。  
> 本版重点：后端 AI 工程能力、会话系统、上下文工程、RAG、Agent、MCP、Eval、部署与面试表达。  
> 前端处理原则：不再教学前端开发细节，仅作为产品化展示与验收层。

---

# 0. 当前项目状态

你的项目当前可按以下状态理解：

```text
已完成：
  - Python 工程基础
  - FastAPI 服务
  - Ollama 调用
  - LLMProvider 初步抽象
  - 配置系统
  - 日志系统
  - 统一异常处理
  - Streaming / SSE 基础接口

已有前端：
  - web/
  - Umi Max
  - Ant Design
  - Ant Design Pro Components
  - Ant Design X
  - Axios
```

因此，后续计划不再重复讲：

```text
如何创建前端页面
如何写 React 组件
如何使用 Ant Design
如何做普通前端状态管理
```

前端只承担：

```text
接口调试
功能展示
面试演示
可视化验收
```

真正的学习重点是：

```text
AI 后端工程
上下文工程
RAG 工程
Agent 工程
MCP 工程
Eval 工程
```

---

# 1. 转型目标

不要把目标定义为：

```text
学习大模型
```

这太宽泛，也容易跑偏。

更准确的目标是：

```text
成为 AI 应用工程师 / AI Agent 工程师
```

你最终要具备这些能力：

```text
能接模型
能做流式输出
能设计多轮会话
能管理上下文窗口
能做文档知识库
能做 Embedding 和向量检索
能做 RAG 问答
能做 Query Rewrite
能做 Agent Tool Calling
能控制 Agent 执行边界
能暴露 MCP Server
能做评测
能部署
能讲清楚架构
```

你不是走下面这条路线：

```text
训练大模型
写论文
研究 Transformer 新结构
做 CUDA Kernel
做分布式训练
```

你走的是：

```text
把模型能力变成企业可用系统
```

---

# 2. 最终项目定位

建议项目定位为：

```text
企业知识库 AI Agent 控制台
```

英文可以叫：

```text
AI Enterprise Copilot
```

或者：

```text
Enterprise RAG Agent
```

核心场景：

```text
上传企业规范文档
  ↓
自动切分 Chunk
  ↓
生成 Embedding
  ↓
写入 pgvector
  ↓
用户在会话中提问
  ↓
系统根据会话历史改写问题
  ↓
RAG 检索相关资料
  ↓
Agent 判断是否需要调用工具
  ↓
模型生成回答
  ↓
返回引用来源、执行轨迹、耗时、模型信息
```

最终你可以向面试官这样描述：

```text
我做了一个面向企业研发规范的 AI Agent 系统。它支持多轮会话、上下文窗口管理、知识库 RAG、Query Rewrite、工具调用、Agent Trace、MCP Server 和评测体系。前端只是作为控制台展示，核心能力在后端和 Agent 编排层。
```

---

# 3. 最终能力链路

完整链路如下：

```text
Chat
  ↓
Conversation
  ↓
Context Window
  ↓
Summary Memory
  ↓
Query Rewrite
  ↓
Document Chunk
  ↓
Embedding
  ↓
Vector Search
  ↓
RAG Answer
  ↓
Agent Tool Calling
  ↓
MCP Server
  ↓
Eval
  ↓
Deploy
```

你当前已经完成的是：

```text
Chat
Streaming
Config
Logger
Exception
```

所以接下来最重要的是：

```text
Conversation
Context Window
Summary Memory
```

也就是会话系统。

---

# 4. 推荐最终目录结构

结合你当前 Python 项目，推荐最终结构如下：

```text
my_python_project/
├── src/
│   └── app/
│       ├── main.py
│       ├── server.py
│       ├── api/
│       │   ├── chat.py
│       │   ├── conversations.py
│       │   ├── messages.py
│       │   ├── documents.py
│       │   ├── rag.py
│       │   ├── agent.py
│       │   └── settings.py
│       ├── core/
│       │   ├── config.py
│       │   ├── logger.py
│       │   ├── exceptions.py
│       │   └── security.py
│       ├── db/
│       │   ├── session.py
│       │   ├── models.py
│       │   └── migrations/
│       ├── schemas/
│       │   ├── chat.py
│       │   ├── conversation.py
│       │   ├── message.py
│       │   ├── document.py
│       │   ├── rag.py
│       │   └── agent.py
│       ├── services/
│       │   ├── llm/
│       │   │   ├── base.py
│       │   │   ├── ollama_provider.py
│       │   │   └── openai_provider.py
│       │   ├── conversation/
│       │   │   ├── conversation_service.py
│       │   │   ├── message_service.py
│       │   │   ├── context_builder.py
│       │   │   └── summarizer.py
│       │   ├── document/
│       │   │   ├── loader.py
│       │   │   ├── splitter.py
│       │   │   └── parser.py
│       │   ├── embedding/
│       │   │   ├── base.py
│       │   │   └── sentence_transformer_provider.py
│       │   ├── rag/
│       │   │   ├── retriever.py
│       │   │   ├── prompt_builder.py
│       │   │   ├── query_rewriter.py
│       │   │   └── pipeline.py
│       │   ├── agent/
│       │   │   ├── loop.py
│       │   │   ├── state.py
│       │   │   ├── planner.py
│       │   │   └── trace.py
│       │   └── tools/
│       │       ├── base.py
│       │       ├── search_docs.py
│       │       ├── read_doc.py
│       │       └── list_docs.py
│       └── utils/
│
├── web/
│   └── ...
│
├── mcp-server/
│   ├── src/
│   │   ├── main.ts
│   │   ├── clients/
│   │   │   └── backend-client.ts
│   │   ├── tools/
│   │   │   ├── search-docs.ts
│   │   │   ├── read-doc.ts
│   │   │   └── ask-agent.ts
│   │   └── schemas/
│   │       └── tool-schemas.ts
│   └── package.json
│
├── docs/
│   ├── architecture.md
│   ├── api-contract.md
│   ├── conversation-design.md
│   ├── context-window-design.md
│   ├── rag-design.md
│   ├── agent-design.md
│   ├── mcp-design.md
│   └── dev-log.md
│
├── eval/
│   ├── cases.json
│   ├── run_eval.py
│   └── report.md
│
├── docker-compose.yml
├── .env.example
└── README.md
```

---

# 5. 总体周计划

因为你已经完成第 2 周，所以从第 3 周开始推进。

```text
Week 1：FastAPI + Ollama 模型调用                    已完成
Week 2：Streaming + 配置 + 日志 + 异常处理             已完成
Week 3：会话系统 Conversation + Message
Week 4：上下文窗口 Context Window + 摘要压缩
Week 5：文档上传 + Chunk 切分
Week 6：Embedding + pgvector
Week 7：RAG 检索 + RAG 问答
Week 8：Query Rewrite + 会话增强 RAG
Week 9：Agent Loop + Tool Calling
Week 10：Agent Trace + 工具日志 + 安全边界
Week 11：MCP Server
Week 12：Eval + Docker + README + 面试包装
```

---

# Week 1：FastAPI + Ollama 模型调用（已完成）

## 阶段目标

完成最小 AI Chat Backend：

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

## 核心知识

```text
FastAPI 路由
Pydantic 请求/响应模型
async / await
httpx
Ollama HTTP API
Provider 抽象
基础错误处理
```

## 已有产物

```text
/chat
LLMProvider
OllamaProvider
基础请求响应模型
```

## 后续可补强

```text
usage 字段预留
latency_ms 统计
provider/model 返回
错误码标准化
```

推荐响应结构：

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

---

# Week 2：Streaming + 配置 + 日志 + 异常（已完成）

## 阶段目标

让模型服务更接近真实 AI 应用：

```text
配置可变
日志可查
支持流式输出
错误可定位
```

## 核心知识

```text
Server-Sent Events
StreamingResponse
pydantic-settings
logging
统一异常处理
```

## 已有产物

```text
.env 配置
Settings
Logger
统一异常处理
/chat/stream
```

## 后续可补强

SSE 建议统一格式：

```text
event: delta
data: {"delta":"你好"}

event: done
data: [DONE]
```

错误返回建议统一：

```json
{
  "error": {
    "code": "LLM_PROVIDER_ERROR",
    "message": "Ollama service unavailable",
    "detail": {}
  }
}
```

---

# Week 3：会话系统 Conversation + Message

## 目标

实现 AI Chat 产品的基础：

```text
多会话
聊天记录
会话历史
多轮对话
```

没有这一层，系统只是：

```text
单轮问答 Demo
```

有了这一层，才是：

```text
真实 AI 助手
```

---

## 要学习的核心概念

### Conversation

一次连续聊天就是一个 conversation。

例如：

```text
会话 A：学习 FastAPI
会话 B：讨论 RAG
会话 C：让 AI 生成组件模板
```

### Message

会话里的每一条消息。

常见 role：

```text
system
user
assistant
tool
```

### 多轮对话

第二轮请求时，不是只传当前问题，而是要带上部分历史消息。

---

## 数据库设计

### conversations 表

```sql
CREATE TABLE conversations (
  id UUID PRIMARY KEY,
  title TEXT NOT NULL,
  summary TEXT,
  model TEXT,
  provider TEXT,
  status TEXT NOT NULL DEFAULT 'active',
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

字段说明：

```text
id：会话 ID
title：会话标题
summary：会话摘要，后续做上下文压缩
model：默认模型
provider：默认模型供应商
status：active / archived / deleted
created_at：创建时间
updated_at：更新时间
```

### messages 表

```sql
CREATE TABLE messages (
  id UUID PRIMARY KEY,
  conversation_id UUID NOT NULL REFERENCES conversations(id),
  role TEXT NOT NULL,
  content TEXT NOT NULL,
  metadata JSONB,
  token_count INT,
  created_at TIMESTAMP DEFAULT NOW()
);
```

metadata 可保存：

```json
{
  "model": "qwen2.5:7b",
  "provider": "ollama",
  "latency_ms": 1200,
  "is_stream": true,
  "sources": [],
  "trace": []
}
```

---

## 后端模块

建议新增：

```text
api/conversations.py
api/messages.py
schemas/conversation.py
schemas/message.py
services/conversation/conversation_service.py
services/conversation/message_service.py
```

---

## API 设计

### 创建会话

```http
POST /conversations
```

请求：

```json
{
  "title": "学习 RAG"
}
```

响应：

```json
{
  "id": "uuid",
  "title": "学习 RAG",
  "summary": null,
  "created_at": "2026-04-30T10:00:00"
}
```

### 查询会话列表

```http
GET /conversations
```

响应：

```json
{
  "items": [
    {
      "id": "uuid",
      "title": "学习 RAG",
      "summary": "这个会话主要讨论 RAG 的 chunk、embedding、检索流程。",
      "updated_at": "2026-04-30T10:20:00"
    }
  ]
}
```

### 查询会话消息

```http
GET /conversations/{conversation_id}/messages
```

响应：

```json
{
  "items": [
    {
      "id": "uuid",
      "role": "user",
      "content": "什么是 RAG？",
      "created_at": "..."
    },
    {
      "id": "uuid",
      "role": "assistant",
      "content": "RAG 是...",
      "metadata": {
        "latency_ms": 1200
      },
      "created_at": "..."
    }
  ]
}
```

### 发送消息

```http
POST /conversations/{conversation_id}/messages
```

请求：

```json
{
  "content": "那 embedding 在里面起什么作用？"
}
```

响应：

```json
{
  "user_message": {
    "id": "uuid",
    "role": "user",
    "content": "那 embedding 在里面起什么作用？"
  },
  "assistant_message": {
    "id": "uuid",
    "role": "assistant",
    "content": "embedding 的作用是...",
    "metadata": {
      "context_message_count": 8,
      "latency_ms": 1800
    }
  }
}
```

### 流式发送消息

```http
POST /conversations/{conversation_id}/messages/stream
```

SSE：

```text
event: message_start
data: {"message_id":"xxx"}

event: delta
data: {"delta":"embedding"}

event: delta
data: {"delta":" 的作用是"}

event: message_end
data: {"message_id":"xxx","content":"embedding 的作用是..."}

event: done
data: [DONE]
```

---

## 实现重点

发送消息流程：

```text
1. 校验 conversation 是否存在
2. 保存 user message
3. 查询最近历史消息
4. 构造 messages
5. 调用 LLM
6. 保存 assistant message
7. 返回结果
```

流式发送消息流程：

```text
1. 保存 user message
2. 查询上下文
3. 调用 LLM stream
4. 边生成边返回 delta
5. 在服务端累积完整 assistant 内容
6. stream 结束后保存 assistant message
```

---

## 验收标准

必须完成：

```text
可以创建会话
可以查看会话列表
可以查看某个会话的历史消息
发送消息后 user 和 assistant 都会入库
第二次提问时模型能理解前面的上下文
流式接口结束后 assistant 完整内容能入库
```

测试对话：

```text
用户：我正在学 FastAPI，记住我刚学到异常处理。
助手：好的，FastAPI 异常处理...
用户：我刚才说我在学什么？
助手：你刚才说你正在学 FastAPI，并提到异常处理。
```

---

# Week 4：上下文窗口 Context Window + 摘要压缩

## 目标

解决真实 AI Chat 的核心问题：

```text
历史消息越来越多，不可能全部塞给模型。
```

所以你要实现：

```text
当前窗口上下文
最近消息裁剪
会话摘要
历史压缩
```

---

## 核心概念

### 当前窗口上下文

每次请求真正传给模型的 messages。

不是所有历史，而是：

```text
system prompt
+ conversation summary
+ recent messages
+ current user message
```

### 为什么不能全量历史

原因：

```text
模型上下文长度有限
成本增加
速度变慢
旧消息噪音变多
容易干扰回答
```

### Summary Memory

把旧消息压缩成摘要，保留关键信息。

---

## ContextBuilder 设计

新增：

```text
services/conversation/context_builder.py
```

核心职责：

```text
输入：conversation、历史 messages、当前用户问题
输出：传给 LLM 的 messages
```

伪代码：

```python
class ContextBuilder:
    def build_context(
        self,
        conversation,
        recent_messages,
        current_user_message: str,
    ) -> list[dict]:
        messages = []

        messages.append({
            "role": "system",
            "content": "你是一个专业的 AI 开发学习助手。"
        })

        if conversation.summary:
            messages.append({
                "role": "system",
                "content": f"以下是当前会话摘要：{conversation.summary}"
            })

        for message in recent_messages:
            messages.append({
                "role": message.role,
                "content": message.content
            })

        messages.append({
            "role": "user",
            "content": current_user_message
        })

        return messages
```

---

## 第一版策略

不要一开始做复杂 token 计算。

第一版先做：

```text
最近 10 条消息
+ 会话摘要
```

配置：

```python
MAX_RECENT_MESSAGES = 10
```

---

## 第二版策略

增加字符数限制：

```python
MAX_CONTEXT_CHARS = 12000
```

裁剪规则：

```text
从最近消息开始往前加
超过 MAX_CONTEXT_CHARS 就停止
summary 永远保留
system prompt 永远保留
```

---

## 第三版策略

增加粗略 token 估算：

```python
def estimate_tokens(text: str) -> int:
    chinese_chars = sum(1 for ch in text if '\u4e00' <= ch <= '\u9fff')
    other_chars = len(text) - chinese_chars
    return chinese_chars + other_chars // 4
```

暂时不用追求精确。

---

## Summarizer 设计

新增：

```text
services/conversation/summarizer.py
```

触发条件：

```text
消息数量 > 20
或者历史字符数 > 15000
```

处理方式：

```text
1. 取较早的 messages
2. 调用 LLM 总结
3. 更新 conversations.summary
4. 保留最近 10 条原始消息
```

摘要 Prompt：

```text
请把以下对话压缩成一段会话摘要，用于后续 AI 继续理解上下文。

要求：
1. 保留用户的核心目标
2. 保留已经确定的技术方案
3. 保留关键代码结构、接口、约束
4. 删除寒暄和重复内容
5. 使用简体中文
6. 不要加入原文中没有的信息

对话内容：
{messages}
```

---

## API 调试接口

建议增加一个调试接口：

```http
GET /conversations/{conversation_id}/context-preview
```

返回：

```json
{
  "conversation_id": "uuid",
  "summary": "...",
  "recent_message_count": 10,
  "estimated_tokens": 3200,
  "messages": [
    {
      "role": "system",
      "content": "..."
    }
  ]
}
```

这个接口非常适合调试和面试演示。

---

## 验收标准

必须完成：

```text
ContextBuilder 可以构造上下文
上下文不会无限增长
可以查看 context preview
超过阈值后能生成 summary
summary 会参与后续对话
```

测试：

```text
连续对话 25 轮
系统仍能回答早期关键信息
但不会把全部历史都塞给模型
```

---

# Week 5：文档上传 + Chunk 切分

## 目标

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

---

## 支持文件类型

第一版只做：

```text
.md
.txt
```

暂时不要做 PDF。

原因：

```text
PDF 解析会严重分散主线
你后续可以单独做 PDF 解析专题
当前重点是 RAG 主链路
```

---

## 数据库设计

### documents 表

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
```

### document_chunks 表

```sql
CREATE TABLE document_chunks (
  id UUID PRIMARY KEY,
  document_id UUID REFERENCES documents(id),
  chunk_index INT NOT NULL,
  content TEXT NOT NULL,
  heading TEXT,
  token_count INT,
  char_count INT,
  metadata JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);
```

---

## Chunk 策略

不要一开始按固定 500 字切。

推荐优先级：

```text
1. Markdown 标题
2. 段落
3. 列表
4. 代码块
5. 固定长度兜底
```

第一版做到：

```text
按 Markdown 标题分组
每组超过 1000 字再按段落切
每个 chunk 保留 heading
```

---

## API 设计

```http
POST /documents/upload
GET /documents
GET /documents/{document_id}
GET /documents/{document_id}/chunks
DELETE /documents/{document_id}
```

上传响应：

```json
{
  "document_id": "uuid",
  "filename": "frontend-style-guide.md",
  "status": "completed",
  "chunk_count": 12
}
```

---

## 验收标准

必须完成：

```text
可以上传 md/txt
可以保存 document
可以生成 chunks
每个 chunk 有 heading
文档有状态：pending / processing / completed / failed
失败时能记录 error_message
```

---

# Week 6：Embedding + pgvector

## 目标

把 chunk 变成可以语义检索的向量。

```text
chunk
  ↓
embedding model
  ↓
vector
  ↓
pgvector
```

---

## 推荐模型

第一版：

```text
sentence-transformers/all-MiniLM-L6-v2
```

原因：

```text
轻量
容易跑
384 维
适合入门
```

后续升级：

```text
BAAI/bge-m3
```

---

## pgvector

docker-compose 示例：

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

启用扩展：

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

---

## Chunk 表增加字段

如果使用 all-MiniLM-L6-v2：

```sql
ALTER TABLE document_chunks
ADD COLUMN embedding VECTOR(384);

ALTER TABLE document_chunks
ADD COLUMN embedding_model TEXT;

ALTER TABLE document_chunks
ADD COLUMN embedding_status TEXT DEFAULT 'pending';

ALTER TABLE document_chunks
ADD COLUMN embedding_error TEXT;
```

注意：

```text
VECTOR(384) 必须和模型维度一致。
```

---

## EmbeddingProvider 抽象

```python
class EmbeddingProvider:
    async def embed_text(self, text: str) -> list[float]:
        raise NotImplementedError

    async def embed_documents(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError
```

---

## 批量处理

不要：

```text
一个 chunk 调一次模型
```

应该：

```text
一次取多个 chunks
批量生成 embeddings
批量写入数据库
```

建议：

```python
BATCH_SIZE = 32
```

---

## API 设计

```http
POST /documents/{document_id}/embed
POST /documents/embed-all
GET /documents/{document_id}/embedding-status
```

---

## 验收标准

必须完成：

```text
每个 chunk 可以生成 embedding
embedding_status 能更新
数据库可以执行向量查询
批量向量化不会一个 chunk 一次提交
```

测试 SQL：

```sql
SELECT
  id,
  content,
  embedding <=> :query_embedding AS distance
FROM document_chunks
ORDER BY embedding <=> :query_embedding
LIMIT 5;
```

---

# Week 7：RAG 检索 + RAG 问答

## 目标

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

---

## RAG Search

API：

```http
POST /rag/search
```

请求：

```json
{
  "query": "React 组件应该如何命名？",
  "top_k": 5,
  "score_threshold": 0.55
}
```

响应：

```json
{
  "query": "React 组件应该如何命名？",
  "chunks": [
    {
      "chunk_id": "uuid",
      "document_id": "uuid",
      "filename": "frontend-style-guide.md",
      "heading": "组件命名",
      "content": "React 组件使用 PascalCase...",
      "score": 0.82
    }
  ]
}
```

---

## RAG Ask

API：

```http
POST /rag/ask
```

请求：

```json
{
  "question": "React 组件应该如何命名？",
  "top_k": 5,
  "score_threshold": 0.55
}
```

响应：

```json
{
  "answer": "React 组件应该使用 PascalCase 命名。",
  "sources": [
    {
      "filename": "frontend-style-guide.md",
      "heading": "组件命名",
      "score": 0.82,
      "chunk_id": "uuid"
    }
  ],
  "trace": {
    "top_k": 5,
    "score_threshold": 0.55,
    "model": "qwen2.5:7b",
    "latency_ms": 1800
  }
}
```

---

## 检索 SQL

```sql
SELECT
  id,
  content,
  metadata,
  1 - (embedding <=> :query_embedding) AS score
FROM document_chunks
WHERE embedding IS NOT NULL
ORDER BY embedding <=> :query_embedding
LIMIT :top_k;
```

---

## Prompt 模板

```text
你是一个企业研发规范助手。

你必须优先根据【资料】回答问题。
如果资料中没有明确答案，请回答：
“根据当前知识库资料，无法确定。”

回答要求：
1. 不要编造资料中不存在的规则
2. 如果能回答，要说明依据来自哪份文档
3. 如果是代码规范问题，尽量给出示例
4. 使用简体中文

【资料】
{context}

【用户问题】
{question}
```

---

## No Answer Policy

必须明确拒答策略。

当满足下面条件时拒答：

```text
没有召回 chunk
最高 score 低于 threshold
资料明显无法回答问题
```

拒答文本：

```text
根据当前知识库资料，无法确定。
```

---

## 验收标准

必须完成：

```text
/rag/search 可以返回 chunks
/rag/ask 可以基于资料回答
回答带 sources
无资料时能拒答
返回 trace
可以调 top_k 和 score_threshold
```

---

# Week 8：Query Rewrite + 会话增强 RAG

## 目标

让 RAG 支持多轮上下文。

普通 RAG 的问题：

```text
用户：React 组件怎么命名？
助手：应该 PascalCase。
用户：那 hooks 呢？
```

如果直接拿“那 hooks 呢？”检索，效果很差。

正确做法：

```text
结合会话历史，把问题改写成：
React hooks 的命名规范是什么？
```

---

## QueryRewriter

新增：

```text
services/rag/query_rewriter.py
```

接口：

```python
class QueryRewriter:
    async def rewrite(
        self,
        conversation_summary: str | None,
        recent_messages: list,
        current_question: str,
    ) -> str:
        ...
```

---

## Rewrite Prompt

```text
请根据会话历史，把用户当前问题改写成一个完整、适合知识库检索的问题。

要求：
1. 不要回答问题
2. 只输出改写后的问题
3. 保留用户真实意图
4. 如果当前问题已经完整，原样输出
5. 使用简体中文

会话摘要：
{summary}

最近对话：
{messages}

当前问题：
{question}
```

---

## 会话增强 RAG 流程

```text
当前问题
  ↓
读取 conversation summary
  ↓
读取最近 messages
  ↓
Query Rewrite
  ↓
用 rewritten_query 做向量检索
  ↓
构造 RAG context
  ↓
带着 recent messages 生成回答
  ↓
保存 assistant message
```

---

## API 设计

```http
POST /conversations/{conversation_id}/rag/ask
```

请求：

```json
{
  "question": "那 hooks 呢？",
  "top_k": 5,
  "score_threshold": 0.55
}
```

响应：

```json
{
  "answer": "...",
  "rewritten_query": "React hooks 的命名规范是什么？",
  "sources": [],
  "trace": {
    "original_query": "那 hooks 呢？",
    "rewritten_query": "React hooks 的命名规范是什么？",
    "context_message_count": 8,
    "retrieved_chunk_count": 5
  }
}
```

---

## 验收标准

必须完成：

```text
支持基于 conversation 的 RAG 问答
能返回 rewritten_query
能返回 original_query
能返回 context_message_count
“那这个呢？”这类问题能正确检索
```

测试：

```text
用户：React 组件怎么命名？
助手：...
用户：那 hooks 呢？
```

系统应该知道第二个问题问的是 React hooks 命名规范。

---

# Week 9：Agent Loop + Tool Calling

## 目标

让系统从“问答”升级为“会使用工具”。

---

## Agent 和 Chat 的区别

普通 Chat：

```text
用户问 -> 模型答
```

RAG Chat：

```text
用户问 -> 检索资料 -> 模型答
```

Agent：

```text
用户问
  ↓
模型判断是否需要工具
  ↓
调用工具
  ↓
读取工具结果
  ↓
可能继续调用工具
  ↓
最终回答
```

---

## Tool 抽象

新增：

```text
services/tools/base.py
```

```python
class Tool:
    name: str
    description: str

    async def run(self, arguments: dict) -> dict:
        raise NotImplementedError
```

---

## 第一批工具

```text
list_docs
search_docs
read_doc
```

### list_docs

作用：

```text
列出知识库文档
```

### search_docs

作用：

```text
根据 query 检索文档 chunk
```

参数：

```json
{
  "query": "React 组件命名规范",
  "top_k": 5
}
```

### read_doc

作用：

```text
读取指定文档
```

参数：

```json
{
  "document_id": "uuid"
}
```

---

## AgentState

```python
class AgentState:
    conversation_id: str
    user_message: str
    messages: list[dict]
    steps: list[dict]
    max_steps: int = 3
    status: str = "running"
```

---

## Agent Loop

流程：

```text
1. 接收用户问题
2. 构造上下文
3. 让模型判断是否需要工具
4. 如果需要，解析 tool_call
5. 执行工具
6. 把工具结果放回 messages
7. 继续让模型判断
8. 达到 final answer 或 max_steps 后结束
```

---

## 降级方案

如果模型 function calling 不稳定，第一版可以做规则版 Agent。

规则：

```text
问题包含“文档 / 规范 / 根据 / 查询”
  -> 调用 search_docs

问题包含“有哪些文档”
  -> 调用 list_docs
```

这样可以先跑通 Agent Loop，不被模型 JSON 输出卡住。

---

## 验收标准

必须完成：

```text
/agent/chat
Tool 抽象
Agent Loop
max_steps 限制
search_docs 工具
list_docs 工具
read_doc 工具
工具结果能回填给模型
```

测试：

```text
根据知识库，帮我生成一个 Button 组件模板。
```

系统应该：

```text
检索规范
读取相关内容
基于工具结果生成回答
```

---

# Week 10：Agent Trace + 工具日志 + 安全边界

## 目标

让 Agent 可观测、可调试、可控制。

---

## 为什么需要 Trace

Agent 最大的问题不是“不会调用工具”，而是：

```text
不知道它为什么调用
不知道它调用了什么
不知道工具返回了什么
不知道哪里失败
不知道为什么循环
```

所以必须记录 trace。

---

## Agent Step 结构

```json
{
  "step": 1,
  "type": "tool_call",
  "tool_name": "search_docs",
  "arguments": {
    "query": "React 组件命名规范"
  },
  "result": {
    "chunks": []
  },
  "latency_ms": 200,
  "success": true
}
```

---

## 工具日志表

```sql
CREATE TABLE tool_call_logs (
  id UUID PRIMARY KEY,
  conversation_id UUID,
  message_id UUID,
  tool_name TEXT NOT NULL,
  arguments JSONB,
  result JSONB,
  success BOOLEAN NOT NULL,
  error_message TEXT,
  latency_ms INT,
  created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 安全边界

必须实现：

```text
max_steps
allowed_tools
tool timeout
retry count
参数校验
错误捕获
```

建议配置：

```python
MAX_AGENT_STEPS = 3
TOOL_TIMEOUT_SECONDS = 10
TOOL_RETRY_COUNT = 1
```

---

## 工具错误处理

工具失败时，不要直接崩掉。

返回结构：

```json
{
  "success": false,
  "error": {
    "code": "TOOL_EXECUTION_ERROR",
    "message": "search_docs timeout"
  }
}
```

---

## API 增强

```http
GET /agent/runs/{run_id}
GET /conversations/{conversation_id}/tool-logs
```

---

## 验收标准

必须完成：

```text
每次工具调用都有 trace
工具调用日志入库
工具失败不导致服务崩溃
max_steps 能阻止死循环
能查看某个会话的工具日志
```

---

# Week 11：MCP Server

## 目标

把你的系统能力开放给外部 AI 工具。

例如：

```text
Claude Desktop
Cursor
GitHub Copilot
其他 MCP Client
```

---

## MCP Server 定位

不要让 MCP Server 直接访问数据库。

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

这样边界清晰：

```text
MCP Server：工具适配层
Backend：业务能力层
DB：数据层
```

---

## MCP 工具设计

第一版只做三个：

```text
search_enterprise_docs
read_enterprise_doc
ask_enterprise_agent
```

---

## 目录结构

```text
mcp-server/
├── src/
│   ├── main.ts
│   ├── clients/
│   │   └── backend-client.ts
│   ├── tools/
│   │   ├── search-docs.ts
│   │   ├── read-doc.ts
│   │   └── ask-agent.ts
│   └── schemas/
│       └── tool-schemas.ts
```

---

## BackendClient

```ts
export class BackendClient {
  constructor(private baseUrl: string) {}

  async searchDocs(query: string, topK = 5) {
    const res = await fetch(`${this.baseUrl}/rag/search`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, top_k: topK }),
    });

    return res.json();
  }
}
```

---

## 工具边界

MCP 工具不要做太多业务逻辑。

它应该只负责：

```text
参数校验
调用 Backend API
格式化返回
```

业务逻辑仍然放在 backend。

---

## 验收标准

必须完成：

```text
MCP Server 可以启动
MCP Inspector 可以看到工具
search_enterprise_docs 能返回知识库结果
ask_enterprise_agent 能调用后端 Agent
README 有 MCP 配置示例
```

---

# Week 12：Eval + Docker + README + 面试包装

## 目标

把项目从“能跑”变成“能展示、能解释、能面试”。

---

## Eval Cases

新增：

```text
eval/cases.json
eval/run_eval.py
eval/report.md
```

示例：

```json
[
  {
    "id": "case_001",
    "type": "rag",
    "question": "React 组件应该如何命名？",
    "expected_keywords": ["PascalCase"],
    "expected_source": "frontend-style-guide.md",
    "must_cite": true
  },
  {
    "id": "case_002",
    "type": "conversation",
    "messages": [
      "我正在学习 FastAPI 异常处理",
      "我刚才说我在学什么？"
    ],
    "expected_keywords": ["FastAPI", "异常处理"]
  },
  {
    "id": "case_003",
    "type": "query_rewrite",
    "messages": [
      "React 组件怎么命名？",
      "那 hooks 呢？"
    ],
    "expected_rewritten_query_keywords": ["React", "hooks", "命名"]
  },
  {
    "id": "case_004",
    "type": "agent",
    "question": "根据知识库帮我生成 Button 组件模板",
    "expected_tools": ["search_docs"],
    "expected_keywords": ["Button"]
  }
]
```

---

## 指标

至少统计：

```text
RAG 命中率
引用来源命中率
关键词命中率
会话记忆命中率
Query Rewrite 正确率
Agent 工具调用成功率
平均响应耗时
错误率
```

---

## Docker Compose

包含：

```text
postgres + pgvector
backend
mcp-server
```

前端可以作为展示层保留，但不是本计划学习重点。

Ollama 可以先作为外部依赖，不强行放入 compose。

---

## README 必须包含

```text
项目背景
解决的问题
技术栈
架构图
核心功能
本地启动
环境变量
接口说明
会话系统设计
上下文窗口设计
RAG 设计
Agent 设计
MCP 使用方式
评测报告
后续规划
```

---

## 面试讲解稿

### 1 分钟版本

```text
我做了一个企业知识库 AI Agent 系统。后端基于 FastAPI，支持 Ollama Provider、流式输出、多会话历史、上下文窗口管理、RAG 检索、Query Rewrite 和 Agent 工具调用。系统可以上传企业规范文档，自动切分、向量化并写入 pgvector，用户提问时会结合会话上下文检索资料并返回引用来源。Agent 部分支持工具调用、执行轨迹、最大步数限制和工具日志。最后我还封装了 MCP Server，让外部 AI 客户端可以复用知识库和 Agent 能力，并通过 eval cases 评估 RAG 命中率、会话记忆和工具调用成功率。
```

### 3 分钟版本结构

```text
1. 项目为什么做
2. 整体架构
3. 会话和上下文怎么处理
4. RAG 怎么实现
5. Agent 怎么调用工具
6. MCP 怎么开放能力
7. 如何评测效果
```

### 5 分钟版本结构

```text
1. 背景：企业知识难以被 AI 准确使用
2. 架构：FastAPI + pgvector + LLM Provider + Agent + MCP
3. 会话：conversation/message/context/summary
4. RAG：document/chunk/embedding/search/prompt/sources
5. Agent：tool schema/loop/max_steps/trace/logs
6. MCP：工具适配层，不直接连 DB
7. Eval：不是靠感觉判断效果，而是有 cases 和指标
8. 展示：控制台只是用于演示核心能力
```

---

# 6. 前端在本计划中的定位

你已经是前端工程师，因此本计划不再展开前端开发教程。

前端只需要满足：

```text
能创建会话
能发送消息
能展示流式回答
能展示历史消息
能上传文档
能展示 RAG sources
能展示 Agent trace
能展示工具日志
能演示项目价值
```

不学习：

```text
如何写页面
如何写组件
如何配置路由
如何用 Ant Design
如何写 CSS
```

前端验收标准：

```text
面试官 5 分钟内能看懂系统价值
```

不是：

```text
前端代码多复杂
UI 多精美
```

---

# 7. 每周固定检查清单

每周结束必须回答：

```text
1. 本周跑通了哪个接口？
2. 本周新增了哪些表？
3. 本周新增了哪些核心服务？
4. 本周遇到的最大问题是什么？
5. 有没有写 dev-log？
6. 有没有更新 README？
7. 有没有可演示功能？
8. 有没有可面试讲点？
9. 有没有失败降级方案？
```

---

# 8. 每日执行节奏

推荐：

```text
20 分钟：复习昨天代码
40 分钟：学一个必要概念
90 分钟：写代码
30 分钟：调试接口
20 分钟：更新 dev-log
```

最低要求：

```text
每天一次 commit
每天一条 dev-log
每两天一个可运行小功能
每周一个可演示结果
```

---

# 9. 风险与降级方案

## Week 3-4 风险：会话系统复杂

风险：

```text
数据库设计不清
消息保存顺序混乱
stream 结束后 assistant 未入库
上下文重复拼接
```

降级：

```text
先只做非流式消息入库
再做流式
先只保留最近 10 条消息
summary 晚 2 天补
```

---

## Week 5-6 风险：pgvector 卡住

风险：

```text
PostgreSQL 配置复杂
pgvector 安装失败
embedding 维度不匹配
模型下载慢
```

降级：

```text
先用内存列表保存 vector
先用 SQLite 保存 chunk
pgvector 卡住不要超过 1 天
先跑通流程再替换存储
```

---

## Week 7-8 风险：RAG 效果差

风险：

```text
chunk 切分差
top_k 不合适
score_threshold 不合适
模型胡编
引用不稳定
```

降级：

```text
先只保证召回正确 chunk
再保证回答正确
最后保证引用稳定
```

---

## Week 9-10 风险：Agent 不稳定

风险：

```text
模型不按 JSON 输出
工具调用格式不稳定
Agent 循环调用
工具失败后中断
```

降级：

```text
先做规则版 Agent
再做模型决策版 Agent
先 max_steps=3
工具失败返回结构化错误
```

---

## Week 11 风险：MCP 调试复杂

风险：

```text
stdio / HTTP 搞混
客户端识别不到工具
schema 写错
```

降级：

```text
先 MCP Inspector 自测
再接 Claude / Cursor / Copilot
MCP 只做工具适配，不做业务逻辑
```

---

## Week 12 风险：包装不足

风险：

```text
功能能跑但讲不清楚
README 太弱
没有评测数据
```

降级：

```text
先写 10 条 eval cases
先写一版 README
先准备 1 分钟讲解稿
```

---

# 10. 最小可交付版本

如果时间不够，最低限度做这个版本：

```text
Backend:
  /conversations
  /conversations/{id}/messages
  /conversations/{id}/messages/stream
  /documents/upload
  /rag/search
  /rag/ask
  /agent/chat

DB:
  conversations
  messages
  documents
  document_chunks
  tool_call_logs

RAG:
  chunk
  embedding
  vector search
  answer with sources

Agent:
  search_docs
  list_docs
  read_doc
  trace
  max_steps

MCP:
  search_enterprise_docs

Eval:
  10 条测试 case
  简单评测报告
```

这个版本已经足够作为转型作品。

---

# 11. 不建议现在重投入的内容

当前不要重投入：

```text
从零训练大模型
复杂微调
GraphRAG
多 Agent 协作
复杂权限系统
PDF 高精度解析
大规模私有化部署
CUDA 优化
分布式推理
复杂前端工程
```

当前最高 ROI：

```text
Conversation
Context Window
RAG
Query Rewrite
Agent
MCP
Eval
```

---

# 12. 面试竞争力排序

完成后，面试优先讲：

## 第一优先级：会话与上下文工程

```text
我不是简单调用模型，而是实现了 conversation/message/context builder/summary memory，可以管理多轮对话和上下文窗口。
```

## 第二优先级：完整 RAG 链路

```text
我从文档上传、chunk、embedding、向量检索、prompt 构造、模型回答、sources 返回做了完整链路。
```

## 第三优先级：Query Rewrite

```text
我处理了多轮问答中的省略问题，例如“那这个呢？”，会先结合会话历史改写为适合检索的问题。
```

## 第四优先级：Agent 工具调用

```text
我实现了 Agent Loop，支持工具调用、执行 trace、最大步数限制、工具失败处理。
```

## 第五优先级：MCP

```text
我把知识库检索和 Agent 能力封装成 MCP Server，让外部 AI 工具可以复用。
```

## 第六优先级：Eval

```text
我不是靠感觉判断效果，而是写了 eval cases，统计 RAG 命中率、引用率、会话记忆、Query Rewrite 和工具调用成功率。
```

---

# 13. 最终你应该能讲清楚的问题

## 模型相关

```text
什么是 token？
什么是 embedding？
chat model 和 embedding model 有什么区别？
为什么要 Provider 抽象？
为什么要 streaming？
Ollama 和 vLLM 有什么区别？
```

## 会话相关

```text
conversation 和 message 如何设计？
为什么不能把所有历史都传给模型？
什么是 context window？
summary memory 解决什么问题？
streaming 时 assistant 消息什么时候入库？
```

## RAG 相关

```text
为什么要 chunk？
chunk size 怎么定？
top_k 怎么定？
score threshold 有什么用？
RAG 为什么能降低幻觉？
RAG 为什么不能完全消除幻觉？
sources 如何返回？
```

## Query Rewrite 相关

```text
为什么“那这个呢？”不能直接检索？
如何根据会话历史改写 query？
改写后的 query 如何参与 RAG？
```

## Agent 相关

```text
Agent 和普通 Chat 有什么区别？
工具调用为什么需要 schema？
Agent Loop 如何停止？
max_steps 为什么重要？
工具失败怎么办？
如何防止 Agent 乱调工具？
```

## MCP 相关

```text
MCP 和 Function Calling 有什么区别？
MCP Server 解决什么问题？
MCP Tool / Resource / Prompt 分别是什么？
为什么 MCP Server 不直接连数据库？
```

## 工程相关

```text
为什么要分 services 层？
为什么要有 trace？
为什么要有 eval？
如何部署？
如何排查问题？
```

---

# 14. 最终结论

你当前最正确的推进顺序是：

```text
已完成：
  FastAPI
  Ollama
  Streaming
  Config
  Logger
  Exception

接下来：
  Conversation
  Context Window
  Summary
  Document Chunk
  Embedding
  RAG
  Query Rewrite
  Agent
  MCP
  Eval
  Deploy
```

不要现在把时间花在前端细节上。

你的核心转型资产应该是：

```text
一个能跑的 AI 后端工程
一套清晰的上下文工程设计
一个完整的 RAG 系统
一个可控的 Agent Loop
一个 MCP Server
一套 Eval 评测报告
一份能讲清楚的 README
```

最终交付不是“学习记录”，而是：

```text
一个可演示、可解释、可面试的 AI Agent 工程项目
```
