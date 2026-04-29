import {
  ChatStreamChunk,
  HistoryItem,
  ModelsResponse,
  clearHistory as apiClearHistory,
  getHistory as apiGetHistory,
  selectModel as apiSelectModel,
  getHealth,
  getModels,
  sendChatStream,
} from '@/services/api';
import { message } from 'antd';
import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
} from 'react';

export type MessageRole = 'user' | 'ai';

export interface TokenUsage {
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
}

export interface ChatMessage {
  id: string;
  role: MessageRole;
  content: string;
  timestamp: number;
  loading?: boolean;
  // AI 响应元信息
  provider?: string;
  model?: string;
  latency_ms?: number;
  usage?: TokenUsage;
}

interface ChatContextType {
  messages: ChatMessage[];
  loading: boolean;
  health: { ok: boolean; message: string } | null;
  healthError: string | null;
  models: ModelsResponse | null;
  modelsError: string | null;
  currentModel: string;
  history: HistoryItem[];
  historyError: string | null;
  historyLoading: boolean;
  sendMessage: (content: string) => Promise<void>;
  loadHistory: () => Promise<void>;
  doClearHistory: () => Promise<void>;
  loadModels: () => Promise<void>;
  handleSelectModel: (model: string) => Promise<void>;
  clearMessages: () => void;
}

const ChatContext = createContext<ChatContextType | null>(null);

export const useChatContext = (): ChatContextType => {
  const ctx = useContext(ChatContext);
  if (!ctx) throw new Error('useChatContext must be used within ChatProvider');
  return ctx;
};

export const ChatProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [health, setHealth] = useState<{ ok: boolean; message: string } | null>(
    null,
  );
  const [healthError, setHealthError] = useState<string | null>(null);
  const [models, setModels] = useState<ModelsResponse | null>(null);
  const [modelsError, setModelsError] = useState<string | null>(null);
  const [currentModel, setCurrentModel] = useState<string>('');
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [historyError, setHistoryError] = useState<string | null>(null);
  const [historyLoading, setHistoryLoading] = useState(false);

  // 页面加载时获取健康状态、模型列表和历史记录
  useEffect(() => {
    (async () => {
      try {
        const h = await getHealth();
        setHealth(h);
        setHealthError(null);
      } catch {
        setHealthError('后端服务不可用，请确认 FastAPI 服务已启动');
        setHealth(null);
      }
    })();

    loadModels();
    loadHistory();
  }, []);

  const loadModels = useCallback(async () => {
    try {
      const data = await getModels();
      setModels(data);
      setCurrentModel(data.current_model);
      setModelsError(null);
    } catch {
      setModelsError('模型列表加载失败');
    }
  }, []);

  const loadHistory = useCallback(async () => {
    setHistoryLoading(true);
    try {
      const data = await apiGetHistory();
      setHistory(data);
      setHistoryError(null);
    } catch {
      setHistoryError('历史记录加载失败');
    } finally {
      setHistoryLoading(false);
    }
  }, []);

  const doClearHistory = useCallback(async () => {
    try {
      const res = await apiClearHistory();
      message.success(res.message || '聊天记录已清空');
      setHistory([]);
      setMessages([]);
    } catch (err: any) {
      const detail = err?.response?.data?.detail;
      message.error(detail || '清空历史失败');
    }
  }, []);

  const handleSelectModel = useCallback(
    async (model: string) => {
      try {
        const res = await apiSelectModel(model);
        if (res.success) {
          setCurrentModel(res.selected_model);
          message.success(res.message || `已切换模型：${res.selected_model}`);
          await loadModels();
        } else {
          message.error(res.message || '模型切换失败');
        }
      } catch (err: any) {
        const detail = err?.response?.data?.detail;
        message.error(detail || '模型切换失败');
      }
    },
    [loadModels],
  );

  const sendMessage = useCallback(
    async (content: string) => {
      if (!content.trim() || loading) return;

      const userMsg: ChatMessage = {
        id: `user-${Date.now()}`,
        role: 'user',
        content: content.trim(),
        timestamp: Date.now(),
      };
      const aiMsgId = `ai-${Date.now() + 1}`;
      const aiMsgPlaceholder: ChatMessage = {
        id: aiMsgId,
        role: 'ai',
        content: '',
        timestamp: Date.now() + 1,
        loading: true,
      };

      setMessages((prev) => [...prev, userMsg, aiMsgPlaceholder]);
      setLoading(true);

      try {
        await sendChatStream(
          {
            message: content.trim(),
            model: currentModel || null,
          },
          (chunk: ChatStreamChunk) => {
            if (chunk.error) {
              throw new Error(
                chunk.error.detail || chunk.error.message || '流式聊天失败',
              );
            }

            setMessages((prev) =>
              prev.map((m) => {
                if (m.id !== aiMsgId) return m;

                const nextContent = `${m.content}${chunk.delta || ''}`;
                const isDone = Boolean(chunk.done);

                return {
                  ...m,
                  content: nextContent,
                  loading: !isDone,
                  provider: 'ollama',
                  model: chunk.model || m.model,
                  latency_ms: chunk.latency_ms ?? m.latency_ms,
                };
              }),
            );
          },
        );

        setMessages((prev) =>
          prev.map((m) =>
            m.id === aiMsgId
              ? {
                  ...m,
                  loading: false,
                }
              : m,
          ),
        );

        // 刷新历史记录
        await loadHistory();
      } catch (err: any) {
        const detail = err?.response?.data?.detail;
        setMessages((prev) =>
          prev.map((m) =>
            m.id === aiMsgId
              ? {
                  ...m,
                  content: detail || '模型调用失败，请检查后端或 Ollama 服务',
                  loading: false,
                }
              : m,
          ),
        );
      } finally {
        setLoading(false);
      }
    },
    [loading, currentModel, loadHistory],
  );

  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  return (
    <ChatContext.Provider
      value={{
        messages,
        loading,
        health,
        healthError,
        models,
        modelsError,
        currentModel,
        history,
        historyError,
        historyLoading,
        sendMessage,
        loadHistory,
        doClearHistory,
        loadModels,
        handleSelectModel,
        clearMessages,
      }}
    >
      {children}
    </ChatContext.Provider>
  );
};
