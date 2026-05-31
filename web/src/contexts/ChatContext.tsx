import {
  AssistantMode,
  AssistantStreamChunk,
  AssistantToolCallEvent,
  ConversationItem,
  MessageItem,
  ModelsResponse,
  createConversation as apiCreateConversation,
  deleteConversation as apiDeleteConversation,
  selectModel as apiSelectModel,
  getConversationMessages,
  getConversations,
  getHealth,
  getModels,
  sendAssistantMessageStream,
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
  assistantRunId?: string;
  agentRunId?: string;
  requestedMode?: AssistantMode;
  resolvedMode?: 'chat' | 'agent';
  routeReason?: string;
  matchedKeywords?: string[];
  toolCalls?: AssistantToolCallEvent[];
  statusText?: string;
}

interface ChatContextType {
  messages: ChatMessage[];
  loading: boolean;
  health: { ok: boolean; message: string } | null;
  healthError: string | null;
  models: ModelsResponse | null;
  modelsError: string | null;
  currentProvider: string;
  currentModel: string;
  conversations: ConversationItem[];
  activeConversationId: string | null;
  activeConversation: ConversationItem | null;
  conversationsLoading: boolean;
  messagesLoading: boolean;
  conversationsError: string | null;
  sendMessage: (
    content: string,
    options?: { mode?: AssistantMode },
  ) => Promise<void>;
  loadConversations: () => Promise<void>;
  createConversation: (title?: string) => Promise<ConversationItem | null>;
  deleteConversation: (conversationId: string) => Promise<void>;
  selectConversation: (conversationId: string) => Promise<void>;
  startNewConversation: () => void;
  loadModels: () => Promise<void>;
  handleSelectProvider: (provider: string) => Promise<void>;
  handleSelectModel: (model: string, provider?: string) => Promise<void>;
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
      typeof metadata.latency_ms === 'number' ? metadata.latency_ms : undefined,
    resolvedMode:
      metadata.mode === 'chat' || metadata.mode === 'agent'
        ? metadata.mode
        : undefined,
  };
}

function getModeLabel(mode?: AssistantMode | 'chat' | 'agent'): string {
  if (mode === 'agent') return 'Agent';
  if (mode === 'chat') return '聊天';
  return '自动';
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
  const [currentProvider, setCurrentProvider] = useState<string>('');
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
      setCurrentProvider(data.current_provider);
      setCurrentModel(data.current_model);
      setModelsError(null);
    } catch {
      setModelsError('模型列表加载失败');
    }
  }, []);

  const getProviderModels = useCallback(
    (provider: string) =>
      models?.providers?.find((item) => item.provider === provider),
    [models],
  );

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
          provider: currentProvider || null,
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
    [currentModel, currentProvider],
  );

  const deleteConversation = useCallback(
    async (conversationId: string) => {
      try {
        await apiDeleteConversation(conversationId);

        setConversations((prev) =>
          prev.filter((item) => item.id !== conversationId),
        );

        if (activeConversationId === conversationId) {
          setActiveConversationId(null);
          setMessages([]);
        }

        message.success('会话已删除');
      } catch (err: any) {
        message.error(getErrorMessage(err, '删除会话失败'));
      }
    },
    [activeConversationId],
  );

  const handleSelectModel = useCallback(
    async (model: string, provider?: string) => {
      const nextProvider = provider || currentProvider;

      try {
        const res = await apiSelectModel(model, nextProvider);
        if (res.success) {
          setCurrentProvider(res.selected_provider || nextProvider);
          setCurrentModel(res.selected_model);
          message.success(
            res.message ||
              `已切换模型：${res.selected_provider}/${res.selected_model}`,
          );
          await loadModels();
        } else {
          message.error(res.message || '模型切换失败');
        }
      } catch (err: any) {
        message.error(getErrorMessage(err, '模型切换失败'));
      }
    },
    [currentProvider, loadModels],
  );

  const handleSelectProvider = useCallback(
    async (provider: string) => {
      const providerModels = getProviderModels(provider);
      const nextModel =
        providerModels?.current_model || providerModels?.available_models[0];

      setCurrentProvider(provider);

      if (!nextModel) {
        setCurrentModel('');
        message.error('该 Provider 暂无可用模型');
        return;
      }

      await handleSelectModel(nextModel, provider);
    },
    [getProviderModels, handleSelectModel],
  );

  const sendMessage = useCallback(
    async (content: string, options?: { mode?: AssistantMode }) => {
      const trimmedContent = content.trim();
      const requestedMode = options?.mode || 'auto';

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
        requestedMode,
        statusText: `${getModeLabel(requestedMode)}模式处理中`,
      };

      setMessages((prev) => [...prev, userMsg, aiMsgPlaceholder]);
      setLoading(true);

      try {
        await sendAssistantMessageStream(
          conversationId,
          {
            message: trimmedContent,
            mode: requestedMode,
            provider: currentProvider || null,
            model: currentModel || null,
          },
          (chunk: AssistantStreamChunk) => {
            if (chunk.event === 'assistant_start') {
              setMessages((prev) =>
                prev.map((m) =>
                  m.id === aiMsgId
                    ? {
                        ...m,
                        assistantRunId: chunk.assistant_run_id || m.id,
                        requestedMode: chunk.requested_mode || requestedMode,
                        resolvedMode: chunk.mode,
                        statusText: chunk.mode
                          ? `${getModeLabel(chunk.mode)}模式处理中`
                          : m.statusText,
                      }
                    : m,
                ),
              );
              return;
            }

            if (chunk.event === 'route_decision') {
              setMessages((prev) =>
                prev.map((m) =>
                  m.id === aiMsgId
                    ? {
                        ...m,
                        resolvedMode: chunk.mode,
                        routeReason: chunk.reason,
                        matchedKeywords: chunk.matched_keywords || [],
                        statusText: `${getModeLabel(chunk.mode)}模式处理中`,
                      }
                    : m,
                ),
              );
              return;
            }

            if (chunk.event === 'tool_call_start') {
              const toolCall: AssistantToolCallEvent = {
                tool_name: chunk.tool_name,
                arguments: chunk.arguments,
                reason: chunk.reason,
                step: chunk.step,
              };

              setMessages((prev) =>
                prev.map((m) =>
                  m.id === aiMsgId
                    ? {
                        ...m,
                        toolCalls: [...(m.toolCalls || []), toolCall],
                        statusText: chunk.tool_name
                          ? `调用工具：${chunk.tool_name}`
                          : '调用工具中',
                      }
                    : m,
                ),
              );
              return;
            }

            if (chunk.event === 'tool_call_end') {
              setMessages((prev) =>
                prev.map((m) =>
                  m.id === aiMsgId
                    ? {
                        ...m,
                        toolCalls: (m.toolCalls || []).map((item) =>
                          item.tool_name === chunk.tool_name &&
                          item.step === chunk.step
                            ? {
                                ...item,
                                success: chunk.success,
                                latency_ms: chunk.latency_ms,
                                error_code: chunk.error_code,
                                error_message: chunk.error_message,
                              }
                            : item,
                        ),
                        statusText: '整理回答中',
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
                        provider:
                          currentProvider ||
                          activeConversation?.provider ||
                          'ollama',
                        model: currentModel || activeConversation?.model,
                        statusText: m.statusText,
                      }
                    : m,
                ),
              );
              return;
            }

            if (chunk.event === 'assistant_end') {
              setMessages((prev) =>
                prev.map((m) =>
                  m.id === aiMsgId
                    ? {
                        ...m,
                        id: chunk.assistant_message_id || m.id,
                        loading: false,
                        assistantRunId: chunk.assistant_run_id,
                        agentRunId: chunk.agent_run_id,
                        resolvedMode: chunk.mode || m.resolvedMode,
                        latency_ms: chunk.latency_ms,
                        toolCalls: chunk.tool_calls || m.toolCalls,
                        provider:
                          chunk.provider ||
                          currentProvider ||
                          activeConversation?.provider,
                        model:
                          chunk.model || currentModel || activeConversation?.model,
                        statusText: undefined,
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
        const latestMessages = await getConversationMessages(conversationId);
        setMessages(
          latestMessages.items
            .map(toChatMessage)
            .filter((item): item is ChatMessage => Boolean(item)),
        );
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
      currentProvider,
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
        currentProvider,
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
        deleteConversation,
        selectConversation,
        startNewConversation,
        loadModels,
        handleSelectProvider,
        handleSelectModel,
        clearMessages,
      }}
    >
      {children}
    </ChatContext.Provider>
  );
};
