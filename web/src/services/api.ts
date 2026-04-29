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
