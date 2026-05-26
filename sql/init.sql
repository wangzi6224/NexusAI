CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
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
    search_vector tsvector setweight(
        to_tsvector('simple', coalesce(heading, '')),
        'A'
    ) || setweight(to_tsvector('simple', content), 'B'),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (document_id, chunk_index)
);
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
CREATE TABLE IF NOT EXISTS messages (
    id TEXT PRIMARY KEY,
    conversation_id TEXT NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
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
CREATE INDEX IF NOT EXISTS idx_documents_updated_at ON documents (updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_document_chunks_document_id ON document_chunks (document_id);
CREATE INDEX IF NOT EXISTS idx_document_chunks_embedding_status ON document_chunks (embedding_status);
CREATE INDEX IF NOT EXISTS idx_document_chunks_embedding_hnsw ON document_chunks USING hnsw (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_conversations_updated_at ON conversations (updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id_created_at ON messages (conversation_id, created_at ASC);
CREATE INDEX IF NOT EXISTS idx_chat_history_created_at ON chat_history (created_at ASC);
CREATE INDEX IF NOT EXISTS idx_document_chunks_search_vector ON document_chunks USING GIN (search_vector);
CREATE INDEX IF NOT EXISTS idx_document_chunks_content_trgm ON document_chunks USING GIN (content gin_trgm_ops);
