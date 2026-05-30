-- =====================================================
-- 应用所需扩展
-- vector：用于保存向量嵌入和近似最近邻搜索
-- pg_trgm：用于模糊文本匹配的 trigram 索引
-- =====================================================
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- =====================================================
-- documents：上传/导入到知识库的源文件记录
-- =====================================================
CREATE TABLE IF NOT EXISTS documents (
    id TEXT PRIMARY KEY,
    filename TEXT NOT NULL,
    file_type TEXT NOT NULL,
    source_path TEXT NOT NULL,
    content TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    chunk_count INTEGER NOT NULL DEFAULT 0,
    char_count INTEGER NOT NULL DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =====================================================
-- document_chunks：文档内容的分块数据，用于检索和向量检索
-- 每条记录对应一个文档块
-- =====================================================
CREATE TABLE IF NOT EXISTS document_chunks (
    id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    heading TEXT,
    content TEXT NOT NULL,
    char_count INTEGER NOT NULL,
    estimated_tokens INTEGER NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    embedding vector(768),
    embedding_model TEXT,
    embedding_status TEXT NOT NULL DEFAULT 'pending',
    embedding_error TEXT,
    embedding_updated_at TIMESTAMPTZ,
    -- 加权全文搜索向量：标题权重高于正文
    search_vector tsvector setweight(
        to_tsvector('simple', coalesce(heading, '')),
        'A'
    ) || setweight(to_tsvector('simple', content), 'B'),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (document_id, chunk_index)
);

-- =====================================================
-- conversations：会话级元信息和摘要记录
-- =====================================================
CREATE TABLE IF NOT EXISTS conversations (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    summary TEXT,
    summarized_message_count INTEGER NOT NULL DEFAULT 0,
    summary_updated_at TIMESTAMPTZ,
    model TEXT NOT NULL,
    provider TEXT NOT NULL DEFAULT 'ollama',
    status TEXT NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =====================================================
-- messages：会话内消息时间线记录
-- =====================================================
CREATE TABLE IF NOT EXISTS messages (
    id TEXT PRIMARY KEY,
    conversation_id TEXT NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =====================================================
-- chat_history：按请求保存的问答日志，用于审计和性能分析
-- =====================================================
CREATE TABLE IF NOT EXISTS chat_history (
    id TEXT PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    model TEXT NOT NULL,
    user_input TEXT NOT NULL,
    prompt TEXT NOT NULL,
    answer TEXT NOT NULL,
    elapsed_seconds DOUBLE PRECISION NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =====================================================
-- agent_runs：每次 Agent 执行的汇总记录
-- 记录执行状态、调用次数、耗时和最终结果
-- =====================================================
CREATE TABLE IF NOT EXISTS agent_runs (
    id TEXT PRIMARY KEY,
    conversation_id TEXT NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    user_message_id TEXT NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
    status TEXT NOT NULL,
    input TEXT NOT NULL,
    final_answer TEXT,
    model TEXT,
    provider TEXT NOT NULL DEFAULT 'ollama',
    max_steps INTEGER NOT NULL DEFAULT 3,
    step_count INTEGER NOT NULL DEFAULT 0,
    total_latency_ms INTEGER,
    error_code TEXT,
    error_message TEXT,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =====================================================
-- agent_steps：每个 Agent 运行步骤的详细跟踪记录
-- =====================================================
CREATE TABLE IF NOT EXISTS agent_steps (
    id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL REFERENCES agent_runs(id) ON DELETE CASCADE,
    step_index INTEGER NOT NULL,
    step_type TEXT NOT NULL,
    thought TEXT,
    reason TEXT,
    tool_name TEXT,
    tool_arguments JSONB NOT NULL DEFAULT '{}'::jsonb,
    tool_result JSONB,
    success BOOLEAN NOT NULL DEFAULT TRUE,
    latency_ms INTEGER NOT NULL DEFAULT 0,
    error_code TEXT,
    error_message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (run_id, step_index)
);

-- =====================================================
-- agent_events：Agent 运行过程中的事件记录，用于可观察性
-- =====================================================
CREATE TABLE IF NOT EXISTS agent_events (
    id TEXT PRIMARY KEY,
    run_id TEXT NOT NULL REFERENCES agent_runs(id) ON DELETE CASCADE,
    step_id TEXT REFERENCES agent_steps(id) ON DELETE SET NULL,
    event_type TEXT NOT NULL,
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =====================================================
-- agent 追踪查询相关索引
-- =====================================================
CREATE INDEX IF NOT EXISTS idx_agent_runs_conversation_id_created_at
ON agent_runs (conversation_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_agent_steps_run_id_step_index
ON agent_steps (run_id, step_index ASC);

CREATE INDEX IF NOT EXISTS idx_agent_events_run_id_created_at
ON agent_events (run_id, created_at ASC);


-- =====================================================
-- assistant_runs：每次 Assistant 调用的汇总记录
-- 记录调用状态、输入输出、耗时和调用细节
-- =====================================================
CREATE TABLE IF NOT EXISTS assistant_runs (
  id TEXT PRIMARY KEY,
  conversation_id TEXT NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
  user_message_id TEXT,
  assistant_message_id TEXT,
  mode TEXT NOT NULL,
  status TEXT NOT NULL,
  input TEXT NOT NULL,
  final_answer TEXT,
  model TEXT,
  provider TEXT,
  latency_ms INTEGER,
  trace JSONB NOT NULL DEFAULT '{}'::jsonb,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- =====================================================
-- 文档检索、向量搜索与会话时间线索引
-- =====================================================
CREATE INDEX IF NOT EXISTS idx_documents_updated_at ON documents (updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_document_chunks_document_id ON document_chunks (document_id);
CREATE INDEX IF NOT EXISTS idx_document_chunks_embedding_status ON document_chunks (embedding_status);
-- HNSW ANN 索引用于 embedding 向量的余弦相似度搜索
CREATE INDEX IF NOT EXISTS idx_document_chunks_embedding_hnsw ON document_chunks USING hnsw (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_conversations_updated_at ON conversations (updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id_created_at ON messages (conversation_id, created_at ASC);
CREATE INDEX IF NOT EXISTS idx_chat_history_created_at ON chat_history (created_at ASC);
-- 用于检索流程的全文和模糊文本索引
CREATE INDEX IF NOT EXISTS idx_document_chunks_search_vector ON document_chunks USING GIN (search_vector);
CREATE INDEX IF NOT EXISTS idx_document_chunks_content_trgm ON document_chunks USING GIN (content gin_trgm_ops);
-- Agent 追踪相关索引
CREATE INDEX IF NOT EXISTS idx_assistant_runs_conversation_id
ON assistant_runs(conversation_id);
-- 按创建时间倒序索引，优化最近调用的查询性能
CREATE INDEX IF NOT EXISTS idx_assistant_runs_created_at
ON assistant_runs(created_at DESC);
-- 状态索引，便于统计不同状态的调用数量和性能分析
CREATE INDEX IF NOT EXISTS idx_assistant_runs_status
ON assistant_runs(status);
