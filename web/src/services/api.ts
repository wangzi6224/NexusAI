import axios from 'axios';

export const API_BASE_URL =
  process.env.UMI_APP_API_BASE_URL || 'http://127.0.0.1:8000';

export const http = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000,
});

// ---- 类型定义 ----

export interface HealthResponse {
  ok: boolean;
  message: string;
}

export interface TokenUsage {
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
}

export interface ChatRequest {
  message: string;
  model?: string | null;
}

export interface ChatResponse {
  answer: string;
  provider: string;
  model: string;
  latency_ms: number;
  usage: TokenUsage;
}

export interface ChatStreamChunk {
  delta?: string;
  done?: boolean;
  model?: string;
  latency_ms?: number;
  error?: {
    code?: string;
    message?: string;
    detail?: string;
  };
}

export interface ConversationItem {
  id: string;
  title: string;
  summary: string | null;
  model: string;
  provider: string;
  status: string;
  message_count: number;
  created_at: string;
  updated_at: string;
}

export interface ConversationListResponse {
  items: ConversationItem[];
}

export type ConversationDetailResponse = ConversationItem;

export type MessageRole = 'system' | 'user' | 'assistant' | 'tool';

export interface MessageItem {
  id: string;
  conversation_id: string;
  role: MessageRole;
  content: string;
  metadata: Record<string, unknown>;
  created_at: string;
}

export interface MessageListResponse {
  items: MessageItem[];
}

export interface ConversationCreateRequest {
  title: string;
  model?: string | null;
}

export interface SendMessageRequest {
  content: string;
  model?: string | null;
}

export interface SendMessageResponse {
  user_message: MessageItem;
  assistant_message: MessageItem;
}

export type ConversationStreamEvent =
  | 'message_start'
  | 'delta'
  | 'message_end'
  | 'error'
  | 'done'
  | 'message';

export interface ConversationStreamChunk {
  event: ConversationStreamEvent;
  delta?: string;
  conversation_id?: string;
  user_message_id?: string;
  assistant_message_id?: string;
  content?: string;
  latency_ms?: number;
  error?: {
    code?: string;
    message?: string;
    detail?: string;
  };
}

export interface HistoryItem {
  timestamp: string;
  model: string;
  user_input: string;
  prompt: string;
  answer: string;
  elapsed_seconds: number;
}

export interface ClearHistoryResponse {
  success: boolean;
  message: string;
}

export interface ModelsResponse {
  current_model: string;
  available_models: string[];
}

export interface SelectModelResponse {
  success: boolean;
  selected_model: string;
  message: string;
}

export interface DocumentItem {
  id: string;
  filename: string;
  file_type: string;
  source_path?: string;
  status: string;
  chunk_count: number;
  char_count: number;
  error_message?: string | null;
  created_at: string;
  updated_at?: string;
}

export interface DocumentListResponse {
  items: DocumentItem[];
}

export interface UploadDocumentResponse {
  document_id: string;
  filename: string;
  file_type: string;
  status: string;
  chunk_count: number;
  char_count: number;
  created_at: string;
}

export interface DocumentChunkItem {
  id: string;
  document_id: string;
  chunk_index: number;
  heading?: string | null;
  content: string;
  char_count: number;
  estimated_tokens: number;
  embedding_status?: string;
  created_at: string;
  updated_at?: string;
  metadata?: Record<string, unknown>;
}

export interface DocumentChunkListResponse {
  items: DocumentChunkItem[];
}

export interface EmbeddingStatusItem {
  chunk_id: string;
  chunk_index: number;
  embedding_status: string;
  embedding_model?: string | null;
  embedding_error?: string | null;
  embedding_updated_at?: string | null;
}

export interface EmbeddingStatusResponse {
  document_id: string;
  items: EmbeddingStatusItem[];
}

export interface EmbedAllDocumentsResponse {
  total_chunks: number;
  embedded_chunks: number;
  failed_chunks: number;
  embedding_model: string;
  status: string;
}

export interface AgentRunItem {
  id: string;
  conversation_id: string;
  user_message_id: string;
  status: string;
  input: string;
  final_answer?: string | null;
  model?: string | null;
  provider: string;
  max_steps: number;
  step_count: number;
  total_latency_ms?: number | null;
  error_code?: string | null;
  error_message?: string | null;
  metadata: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface AgentStepItem {
  id: string;
  run_id: string;
  step_index: number;
  step_type: string;
  thought?: string | null;
  reason?: string | null;
  tool_name?: string | null;
  tool_arguments: Record<string, unknown>;
  tool_result?: Record<string, unknown> | null;
  success: boolean;
  latency_ms: number;
  error_code?: string | null;
  error_message?: string | null;
  created_at: string;
}

export interface AgentEventItem {
  id: string;
  run_id: string;
  step_id?: string | null;
  event_type: string;
  payload: Record<string, unknown>;
  created_at: string;
}

export interface AgentRunListResponse {
  conversation_id: string;
  runs: AgentRunItem[];
}

export interface AgentRunDetailResponse {
  run: AgentRunItem;
  steps: AgentStepItem[];
  events: AgentEventItem[];
}

// ---- API 函数 ----

export async function getHealth(): Promise<HealthResponse> {
  const { data } = await http.get<HealthResponse>('/health');
  return data;
}

export async function sendChat(payload: ChatRequest): Promise<ChatResponse> {
  const { data } = await http.post<ChatResponse>('/chat', payload);
  return data;
}

export async function sendChatStream(
  payload: ChatRequest,
  onChunk: (chunk: ChatStreamChunk) => void,
): Promise<void> {
  const streamUrl = process.env.UMI_APP_STREAM_API_URL || '/api/chat/stream';

  const response = await fetch(streamUrl, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'text/event-stream',
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `HTTP ${response.status}`);
  }

  if (!response.body) {
    throw new Error('流式响应为空');
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder('utf-8');
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const events = buffer.split('\n\n');
    buffer = events.pop() || '';

    for (const event of events) {
      const lines = event
        .split('\n')
        .map((line) => line.trim())
        .filter((line) => line.startsWith('data:'));

      for (const line of lines) {
        const data = line.slice(5).trim();

        if (!data) continue;
        if (data === '[DONE]') return;

        try {
          onChunk(JSON.parse(data) as ChatStreamChunk);
        } catch {
          // 忽略非 JSON 的 SSE 数据
        }
      }
    }
  }
}

function buildApiUrl(path: string): string {
  const baseUrl = API_BASE_URL;

  if (!baseUrl) return `/api${path}`;

  return `${baseUrl.replace(/\/$/, '')}${path}`;
}

function parseSseEvent(event: string): { event: string; data: string } | null {
  let eventName = 'message';
  const dataLines: string[] = [];

  event.split('\n').forEach((line) => {
    const trimmedLine = line.trim();

    if (trimmedLine.startsWith('event:')) {
      eventName = trimmedLine.slice(6).trim() || 'message';
    }

    if (trimmedLine.startsWith('data:')) {
      dataLines.push(trimmedLine.slice(5).trim());
    }
  });

  if (dataLines.length === 0) return null;

  return {
    event: eventName,
    data: dataLines.join('\n'),
  };
}

export async function createConversation(
  payload: ConversationCreateRequest,
): Promise<ConversationDetailResponse> {
  const { data } = await http.post<ConversationDetailResponse>(
    '/conversations',
    payload,
  );
  return data;
}

export async function getConversations(): Promise<ConversationListResponse> {
  const { data } = await http.get<ConversationListResponse>('/conversations');
  return data;
}

export async function getConversation(
  conversationId: string,
): Promise<ConversationDetailResponse> {
  const { data } = await http.get<ConversationDetailResponse>(
    `/conversations/${conversationId}`,
  );
  return data;
}

export async function getConversationMessages(
  conversationId: string,
): Promise<MessageListResponse> {
  const { data } = await http.get<MessageListResponse>(
    `/conversations/${conversationId}/messages`,
  );
  return data;
}

export async function sendConversationMessage(
  conversationId: string,
  payload: SendMessageRequest,
): Promise<SendMessageResponse> {
  const { data } = await http.post<SendMessageResponse>(
    `/conversations/${conversationId}/messages`,
    payload,
  );
  return data;
}

export async function sendConversationMessageStream(
  conversationId: string,
  payload: SendMessageRequest,
  onChunk: (chunk: ConversationStreamChunk) => void,
): Promise<void> {
  const response = await fetch(
    buildApiUrl(`/conversations/${conversationId}/messages/stream`),
    {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'text/event-stream',
      },
      body: JSON.stringify(payload),
    },
  );

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `HTTP ${response.status}`);
  }

  if (!response.body) {
    throw new Error('流式响应为空');
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder('utf-8');
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const events = buffer.split('\n\n');
    buffer = events.pop() || '';

    for (const rawEvent of events) {
      const parsedEvent = parseSseEvent(rawEvent);

      if (!parsedEvent) continue;
      if (parsedEvent.data === '[DONE]') {
        onChunk({ event: 'done' });
        return;
      }

      try {
        const data = JSON.parse(parsedEvent.data);

        if (parsedEvent.event === 'error') {
          onChunk({
            event: 'error',
            error: data,
          });
          continue;
        }

        onChunk({
          event: parsedEvent.event as ConversationStreamEvent,
          ...data,
        });
      } catch {
        // 忽略非 JSON 的 SSE 数据
      }
    }
  }
}

export async function getHistory(): Promise<HistoryItem[]> {
  const { data } = await http.get<HistoryItem[]>('/history');
  return data;
}

export async function clearHistory(): Promise<ClearHistoryResponse> {
  const { data } = await http.post<ClearHistoryResponse>('/history/clear');
  return data;
}

export async function getModels(): Promise<ModelsResponse> {
  const { data } = await http.get<ModelsResponse>('/models');
  return data;
}

export async function selectModel(model: string): Promise<SelectModelResponse> {
  const { data } = await http.post<SelectModelResponse>('/model/select', {
    model,
  });
  return data;
}

export async function uploadDocument(
  file: File,
): Promise<UploadDocumentResponse> {
  const formData = new FormData();
  formData.append('file', file);

  const { data } = await http.post<UploadDocumentResponse>(
    '/documents/upload',
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    },
  );

  return data;
}

export async function getDocuments(): Promise<DocumentListResponse> {
  const { data } = await http.get<DocumentListResponse>('/documents');
  return data;
}

export async function triggerDocumentSplit(documentId: string): Promise<void> {
  await http.post(`/documents/${documentId}/split`);
}

export async function getDocumentChunks(
  documentId: string,
): Promise<DocumentChunkListResponse> {
  const { data } = await http.get<DocumentChunkListResponse>(
    `/documents/${documentId}/chunks`,
  );

  return data;
}

export async function getDocumentEmbeddingStatus(
  documentId: string,
): Promise<EmbeddingStatusResponse> {
  const { data } = await http.get<EmbeddingStatusResponse>(
    `/documents/${documentId}/embedding-status`,
  );

  return data;
}

export async function embedAllDocuments(): Promise<EmbedAllDocumentsResponse> {
  const { data } = await http.post<EmbedAllDocumentsResponse>(
    '/documents/embed-all',
  );

  return data;
}

export async function getAgentRuns(
  conversationId: string,
): Promise<AgentRunListResponse> {
  const { data } = await http.get<AgentRunListResponse>(
    `/agent/conversations/${conversationId}/runs`,
  );

  return data;
}

export async function getAgentRunDetail(
  runId: string,
): Promise<AgentRunDetailResponse> {
  const { data } = await http.get<AgentRunDetailResponse>(
    `/agent/runs/${runId}`,
  );

  return data;
}
