import {
  createSession as createSessionAPI,
  getSessionDetail,
  streamChat,
  submitFeedback as submitFeedbackAPI,
} from '@/services/chat';
import { history, useModel, useParams } from '@umijs/max';
import { message } from 'antd';
import React, {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
} from 'react';

export type MessageRole = 'user' | 'ai';

export interface ChatMessage {
  id: string;
  role: MessageRole;
  content: string;
  timestamp: number;
  streaming?: boolean;
  loading?: boolean;
  messageId?: number;
  helpful?: boolean;
  isComplete?: boolean;
}

export interface Conversation {
  id: string;
  title: string;
  messages: ChatMessage[];
  createdAt: number;
  relatedQuestion?: string;
}

export type CategoryOption = {
  label:
    | '全部'
    | '上交所主板'
    | '上交所科创板'
    | '深交所主板'
    | '深交所创业板'
    | '北交所';
  value: 'all' | 'sse_main' | 'sse_star' | 'szse_main' | 'szse_star' | 'bse';
};

export const CATEGORY_OPTIONS: CategoryOption[] = [
  { label: '全部', value: 'all' },
  { label: '上交所主板', value: 'sse_main' },
  { label: '上交所科创板', value: 'sse_star' },
  { label: '深交所主板', value: 'szse_main' },
  { label: '深交所创业板', value: 'szse_star' },
  { label: '北交所', value: 'bse' },
];

const PENDING_Q_KEY = '_lawai_pending_q';

interface ChatContextType {
  conversations: Conversation[];
  activeConversationId: string | null;
  networkEnabled: boolean;
  selectedCategory: string;
  loadingSession: boolean;
  setNetworkEnabled: (enabled: boolean) => void;
  setSelectedCategory: (category: string) => void;
  createNewConversation: () => void;
  setActiveConversationId: (id: string | null) => void;
  sendMessage: (content: string) => void;
  stopStream: () => void;
  activeConversation: Conversation | null;
  submitFeedback: (messageId: number, helpful: boolean) => Promise<void>;
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
  const { initialState, refresh } = useModel('@@initialState');
  const params = useParams<{ sessionId?: string }>();
  const sessionId = params.sessionId
    ? parseInt(params.sessionId, 10) || null
    : null;

  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeMessages, setActiveMessages] = useState<ChatMessage[]>([]);
  const [loadingSession, setLoadingSession] = useState(false);
  const [networkEnabled, setNetworkEnabled] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState('all');

  const streamCleanupRef = useRef<(() => void) | null>(null);
  const refreshTitleTimerRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    const sessions = (initialState as any)?.sessions as
      | Array<{ session_id: number; title: string; updated_at: number }>
      | undefined;
    if (sessions?.length) {
      setConversations(
        sessions.map((s) => ({
          id: String(s.session_id),
          title: s.title,
          messages: [],
          createdAt: s.updated_at * 1000,
        })),
      );
    }
  }, [initialState]);

  useEffect(() => {
    const savedNet = localStorage.getItem('networkEnabled');
    const savedCat = localStorage.getItem('selectedCategory');
    if (savedNet !== null) {
      setNetworkEnabled(savedNet !== 'false');
    }
    if (savedCat) {
      setSelectedCategory(savedCat);
    }
  }, []);

  // 清理定时器
  useEffect(() => {
    return () => {
      if (refreshTitleTimerRef.current) {
        clearTimeout(refreshTitleTimerRef.current);
      }
    };
  }, []);

  const startStreaming = useCallback(
    (targetSessionId: number, content: string, net: boolean, cat: string) => {
      const userMsg: ChatMessage = {
        id: `local-user-${Date.now()}`,
        role: 'user',
        content,
        timestamp: Date.now(),
      };
      const aiMsgLocalId = `local-ai-${Date.now()}`;
      const aiMsg: ChatMessage = {
        id: aiMsgLocalId,
        role: 'ai',
        content: '',
        timestamp: Date.now() + 1,
        loading: true,
        streaming: false,
      };

      setActiveMessages((prev) => [...prev, userMsg, aiMsg]);

      streamCleanupRef.current = streamChat(
        {
          session_id: targetSessionId,
          question: content,
          enable_web_search: net,
          sector: cat,
        },
        {
          onChunk: (accumulated) => {
            setActiveMessages((prev) =>
              prev.map((m) =>
                m.id === aiMsgLocalId
                  ? {
                      ...m,
                      content: accumulated,
                      loading: false,
                      streaming: true,
                    }
                  : m,
              ),
            );
          },
          onDone: (messageId) => {
            setActiveMessages((prev) =>
              prev.map((m) =>
                m.id === aiMsgLocalId
                  ? {
                      ...m,
                      loading: false,
                      streaming: false,
                      ...(messageId > 0 ? { messageId, isComplete: true } : {}),
                    }
                  : m,
              ),
            );
            streamCleanupRef.current = null;
            // 延迟刷新列表以获取后端生成的标题
            if (refreshTitleTimerRef.current) {
              clearTimeout(refreshTitleTimerRef.current);
            }
            refreshTitleTimerRef.current = setTimeout(() => {
              refresh();
              refreshTitleTimerRef.current = null;
            }, 500);
          },
          onError: (err) => {
            console.error('Stream error:', err);
            setActiveMessages((prev) =>
              prev.map((m) =>
                m.id === aiMsgLocalId
                  ? {
                      ...m,
                      content: '抱歉，获取回答时发生错误，请稍后重试。',
                      loading: false,
                      streaming: false,
                    }
                  : m,
              ),
            );
            streamCleanupRef.current = null;
          },
        },
      );
    },
    [],
  );

  // Load session messages when sessionId changes (URL-driven)
  useEffect(() => {
    if (!sessionId) {
      setActiveMessages([]);
      return;
    }

    streamCleanupRef.current?.();
    streamCleanupRef.current = null;

    const pendingRaw = sessionStorage.getItem(PENDING_Q_KEY);
    if (pendingRaw) {
      try {
        const pending = JSON.parse(pendingRaw);
        if (pending.sessionId === sessionId) {
          sessionStorage.removeItem(PENDING_Q_KEY);
          setConversations((prev) => {
            if (prev.find((c) => c.id === String(sessionId))) return prev;
            return [
              {
                id: String(sessionId),
                title: '新对话',
                messages: [],
                createdAt: Date.now(),
              },
              ...prev,
            ];
          });
          setActiveMessages([]);
          startStreaming(
            sessionId,
            pending.content,
            pending.networkEnabled,
            pending.selectedCategory,
          );
          return;
        }
      } catch {
        sessionStorage.removeItem(PENDING_Q_KEY);
      }
    }

    setLoadingSession(true);
    setActiveMessages([]);

    getSessionDetail(sessionId)
      .then((res) => {
        if (res.code === 0) {
          const msgs: ChatMessage[] = res.data.messages.map((m) => ({
            id: String(m.id),
            role: (m.role === 'assistant' ? 'ai' : 'user') as MessageRole,
            content: m.content,
            timestamp: m.created_at * 1000,
            messageId: m.id,
            isComplete: m.is_complete,
            helpful: m.helpful,
          }));
          setActiveMessages(msgs);
          setConversations((prev) => {
            const exists = prev.find((c) => c.id === String(sessionId));
            if (!exists) {
              return [
                {
                  id: String(sessionId),
                  title: res.data.title,
                  messages: [],
                  createdAt: Date.now(),
                },
                ...prev,
              ];
            }
            return prev.map((c) =>
              c.id === String(sessionId) ? { ...c, title: res.data.title } : c,
            );
          });
        }
      })
      .catch(() => {})
      .finally(() => {
        setLoadingSession(false);
      });
  }, [sessionId, startStreaming]);

  const activeConversationId = sessionId ? String(sessionId) : null;

  const activeConversation = useMemo((): Conversation | null => {
    if (!sessionId) return null;
    const session = conversations.find((c) => c.id === String(sessionId));
    return {
      id: String(sessionId),
      title: session?.title ?? '',
      messages: activeMessages,
      createdAt: session?.createdAt ?? Date.now(),
    };
  }, [sessionId, conversations, activeMessages]);

  const createNewConversation = useCallback(() => {
    streamCleanupRef.current?.();
    streamCleanupRef.current = null;
    refresh();
    history.push('/lawai-chat');
  }, []);

  const setActiveConversationId = useCallback((id: string | null) => {
    streamCleanupRef.current?.();
    streamCleanupRef.current = null;
    if (id) {
      history.push(`/lawai-chat/${id}`);
    } else {
      history.push('/lawai-chat');
    }
  }, []);

  const stopStream = useCallback(() => {
    streamCleanupRef.current?.();
    streamCleanupRef.current = null;
    setActiveMessages((prev) =>
      prev.map((m) =>
        m.loading || m.streaming
          ? { ...m, loading: false, streaming: false }
          : m,
      ),
    );
    // 延迟刷新列表以获取后端生成的标题
    if (refreshTitleTimerRef.current) {
      clearTimeout(refreshTitleTimerRef.current);
    }
    refreshTitleTimerRef.current = setTimeout(() => {
      refresh();
      refreshTitleTimerRef.current = null;
    }, 500);
  }, [refresh]);

  const sendMessage = useCallback(
    async (content: string) => {
      if (!content.trim()) return;

      streamCleanupRef.current?.();
      streamCleanupRef.current = null;

      if (sessionId) {
        startStreaming(sessionId, content, networkEnabled, selectedCategory);
      } else {
        try {
          const res = await createSessionAPI({
            enable_web_search: networkEnabled,
            sector: selectedCategory,
          });

          if (res.code !== 0) {
            message.error(res.msg || '创建会话失败');
            return;
          }

          const newSessionId = res.data.session_id;

          sessionStorage.setItem(
            PENDING_Q_KEY,
            JSON.stringify({
              sessionId: newSessionId,
              content,
              networkEnabled,
              selectedCategory,
            }),
          );

          history.push(`/lawai-chat/${newSessionId}`);
        } catch {}
      }
    },
    [sessionId, networkEnabled, selectedCategory, startStreaming],
  );

  const submitFeedback = useCallback(
    async (messageId: number, helpful: boolean) => {
      if (!sessionId) return;
      await submitFeedbackAPI({
        message_id: messageId,
        session_id: sessionId,
        helpful,
      });
      setActiveMessages((prev) =>
        prev.map((m) => (m.messageId === messageId ? { ...m, helpful } : m)),
      );
    },
    [sessionId],
  );

  return (
    <ChatContext.Provider
      value={{
        conversations,
        activeConversationId,
        networkEnabled,
        selectedCategory,
        loadingSession,
        setNetworkEnabled,
        setSelectedCategory,
        createNewConversation,
        setActiveConversationId,
        sendMessage,
        stopStream,
        activeConversation,
        submitFeedback,
      }}
    >
      {children}
    </ChatContext.Provider>
  );
};
