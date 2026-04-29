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

// ---- API 函数 ----

export async function getHealth (): Promise<HealthResponse> {
  const { data } = await http.get<HealthResponse>('/health');
  return data;
}

export async function sendChat (payload: ChatRequest): Promise<ChatResponse> {
  const { data } = await http.post<ChatResponse>('/chat', payload);
  return data;
}

export async function sendChatStream (
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

export async function getHistory (): Promise<HistoryItem[]> {
  const { data } = await http.get<HistoryItem[]>('/history');
  return data;
}

export async function clearHistory (): Promise<ClearHistoryResponse> {
  const { data } = await http.post<ClearHistoryResponse>('/history/clear');
  return data;
}

export async function getModels (): Promise<ModelsResponse> {
  const { data } = await http.get<ModelsResponse>('/models');
  return data;
}

export async function selectModel (model: string): Promise<SelectModelResponse> {
  const { data } = await http.post<SelectModelResponse>('/model/select', {
    model,
  });
  return data;
}
