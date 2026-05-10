import {
  ConversationItem,
  ConversationStreamChunk,
  MessageItem,
  ModelsResponse,
  createConversation as apiCreateConversation,
  getConversationMessages,
  getConversations,
  getHealth,
  getModels,
  selectModel as apiSelectModel,
  sendConversationMessageStream,
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
  conversations: ConversationItem[];
  activeConversationId: string | null;
  activeConversation: ConversationItem | null;
  conversationsLoading: boolean;
  messagesLoading: boolean;
  conversationsError: string | null;
  sendMessage: (content: string) => Promise<void>;
  loadConversations: () => Promise<void>;
  createConversation: (title?: string) => Promise<ConversationItem | null>;
  selectConversation: (conversationId: string) => Promise<void>;
  startNewConversation: () => void;
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

function getErrorMessage(err: any, fallback: string): string {
  return (
    err?.response?.data?.detail ||
    err?.response?.data?.message ||
    err?.message ||
    fallback
  );
}

function buildConversationTitle(content: string): string {
  const title = content.trim().replace(/\s+/g, ' ');

  if (title.length <= 24) return title;

  return `${title.slice(0, 24)}...`;
}

function toChatMessage(item: MessageItem): ChatMessage | null {
  if (item.role !== 'user' && item.role !== 'assistant') return null;

  const metadata = item.metadata || {};

  return {
    id: item.id,
    role: item.role === 'assistant' ? 'ai' : 'user',
    content: item.content,
    timestamp: new Date(item.created_at).getTime(),
    provider:
      typeof metadata.provider === 'string' ? metadata.provider : undefined,
    model: typeof metadata.model === 'string' ? metadata.model : undefined,
    latency_ms:
      typeof metadata.latency_ms === 'number'
        ? metadata.latency_ms
        : undefined,
  };
}

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
  const [conversations, setConversations] = useState<ConversationItem[]>([]);
  const [activeConversationId, setActiveConversationId] = useState<
    string | null
  >(null);
  const [conversationsLoading, setConversationsLoading] = useState(false);
  const [messagesLoading, setMessagesLoading] = useState(false);
  const [conversationsError, setConversationsError] = useState<string | null>(
    null,
  );

  const activeConversation =
    conversations.find((item) => item.id === activeConversationId) || null;

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

  const loadConversations = useCallback(async () => {
    setConversationsLoading(true);
    try {
      const data = await getConversations();
      setConversations(data.items);
      setConversationsError(null);
    } catch (err: any) {
      setConversationsError(getErrorMessage(err, '会话列表加载失败'));
    } finally {
      setConversationsLoading(false);
    }
  }, []);

  const selectConversation = useCallback(async (conversationId: string) => {
    setActiveConversationId(conversationId);
    setMessages([]);
    setMessagesLoading(true);

    try {
      const data = await getConversationMessages(conversationId);
      setMessages(
        data.items
          .map(toChatMessage)
          .filter((item): item is ChatMessage => Boolean(item)),
      );
      setConversationsError(null);
    } catch (err: any) {
      setConversationsError(getErrorMessage(err, '会话消息加载失败'));
    } finally {
      setMessagesLoading(false);
    }
  }, []);

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
    loadConversations();
  }, [loadConversations, loadModels]);

  const createConversation = useCallback(
    async (title = '新会话'): Promise<ConversationItem | null> => {
      try {
        const conversation = await apiCreateConversation({
          title,
          model: currentModel || null,
        });

        setConversations((prev) => [
          conversation,
          ...prev.filter((item) => item.id !== conversation.id),
        ]);
        setActiveConversationId(conversation.id);
        setMessages([]);
        setConversationsError(null);

        return conversation;
      } catch (err: any) {
        message.error(getErrorMessage(err, '创建会话失败'));
        return null;
      }
    },
    [currentModel],
  );

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
        message.error(getErrorMessage(err, '模型切换失败'));
      }
    },
    [loadModels],
  );

  const sendMessage = useCallback(
    async (content: string) => {
      const trimmedContent = content.trim();

      if (!trimmedContent || loading) return;

      let conversationId = activeConversationId;

      if (!conversationId) {
        const conversation = await createConversation(
          buildConversationTitle(trimmedContent),
        );

        if (!conversation) return;

        conversationId = conversation.id;
      }

      const userMsg: ChatMessage = {
        id: `user-${Date.now()}`,
        role: 'user',
        content: trimmedContent,
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
        await sendConversationMessageStream(
          conversationId,
          {
            content: trimmedContent,
            model: currentModel || null,
          },
          (chunk: ConversationStreamChunk) => {
            if (chunk.event === 'message_start' && chunk.user_message_id) {
              setMessages((prev) =>
                prev.map((m) =>
                  m.id === userMsg.id
                    ? {
                        ...m,
                        id: chunk.user_message_id || m.id,
                      }
                    : m,
                ),
              );
              return;
            }

            if (chunk.event === 'error' || chunk.error) {
              throw new Error(
                chunk.error?.detail ||
                  chunk.error?.message ||
                  '流式会话消息失败',
              );
            }

            if (chunk.event === 'delta') {
              setMessages((prev) =>
                prev.map((m) =>
                  m.id === aiMsgId
                    ? {
                        ...m,
                        content: `${m.content}${chunk.delta || ''}`,
                        loading: true,
                        provider: activeConversation?.provider || 'ollama',
                        model: currentModel || activeConversation?.model,
                      }
                    : m,
                ),
              );
              return;
            }

            if (chunk.event === 'message_end') {
              setMessages((prev) =>
                prev.map((m) =>
                  m.id === aiMsgId
                    ? {
                        ...m,
                        id: chunk.assistant_message_id || m.id,
                        content: chunk.content || m.content,
                        loading: false,
                        latency_ms: chunk.latency_ms,
                        provider: activeConversation?.provider || 'ollama',
                        model: currentModel || activeConversation?.model,
                      }
                    : m,
                ),
              );
            }
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

        await loadConversations();
      } catch (err: any) {
        setMessages((prev) =>
          prev.map((m) =>
            m.id === aiMsgId
              ? {
                  ...m,
                  content: getErrorMessage(
                    err,
                    '模型调用失败，请检查后端或 Ollama 服务',
                  ),
                  loading: false,
                }
              : m,
          ),
        );
      } finally {
        setLoading(false);
      }
    },
    [
      activeConversation,
      activeConversationId,
      createConversation,
      currentModel,
      loadConversations,
      loading,
    ],
  );

  const clearMessages = useCallback(() => {
    setMessages([]);
  }, []);

  const startNewConversation = useCallback(() => {
    setActiveConversationId(null);
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
        conversations,
        activeConversationId,
        activeConversation,
        conversationsLoading,
        messagesLoading,
        conversationsError,
        sendMessage,
        loadConversations,
        createConversation,
        selectConversation,
        startNewConversation,
        loadModels,
        handleSelectModel,
        clearMessages,
      }}
    >
      {children}
    </ChatContext.Provider>
  );
};
