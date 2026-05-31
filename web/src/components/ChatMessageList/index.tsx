import ToolCallTimeline from '@/components/ToolCallTimeline';
import TraceDrawer from '@/components/TraceDrawer';
import { ChatMessage } from '@/contexts/ChatContext';
import type { BubbleProps } from '@ant-design/x';
import { Bubble } from '@ant-design/x';
import { XMarkdown } from '@ant-design/x-markdown';
import { Space, Tag, Typography } from 'antd';
import React, { useMemo } from 'react';
import styles from './index.module.less';

const { Text } = Typography;

interface ChatMessageListProps {
  messages: ChatMessage[];
  loading?: boolean;
}

const renderMarkdown = (content: unknown) => (
  <XMarkdown
    content={String(content ?? '')}
    components={{
      a: (props) => <a {...props} target="_blank" rel="noopener noreferrer" />,
    }}
  />
);

type BubbleItem = BubbleProps & { key: string; role: string };

const ChatMessageList: React.FC<ChatMessageListProps> = ({
  messages,
  loading = false,
}) => {
  const items = useMemo(
    () =>
      messages.map((msg): BubbleItem => {
        // loading=true 且无内容：等待第一个 token，显示 spinner
        // loading=true 且有内容：SSE 流式接收中，用 streaming prop 渲染
        // loading=false：流式完成
        const isWaiting = Boolean(msg.loading) && !msg.content;
        const isStreaming = Boolean(msg.loading) && Boolean(msg.content);

        const item: BubbleItem = {
          key: msg.id,
          role: msg.role,
          content: msg.content,
          loading: isWaiting,
          streaming: isStreaming,
        };

        if (msg.role === 'ai' && !isWaiting) {
          item.contentRender = renderMarkdown;

          const metaParts: string[] = [];
          if (msg.model) metaParts.push(msg.model);
          if (msg.provider) metaParts.push(msg.provider);
          if (msg.latency_ms !== null && msg.latency_ms !== undefined)
            metaParts.push(`${msg.latency_ms} ms`);
          if (
            msg.usage?.total_tokens !== null &&
            msg.usage?.total_tokens !== undefined
          )
            metaParts.push(`${msg.usage.total_tokens} tokens`);

          const toolCount = msg.toolCalls?.length || 0;

          if (
            msg.resolvedMode ||
            msg.statusText ||
            toolCount > 0 ||
            metaParts.length > 0 ||
            msg.assistantRunId
          ) {
            item.footer = (
              <Space size={6} wrap className={styles.metaLine}>
                {msg.resolvedMode ? (
                  <Tag
                    color={msg.resolvedMode === 'agent' ? 'processing' : 'cyan'}
                    className={styles.metaTag}
                  >
                    {msg.resolvedMode === 'agent' ? 'Agent' : '聊天'}
                  </Tag>
                ) : null}
                {toolCount > 0 ? (
                  <Tag color="purple" className={styles.metaTag}>
                    工具 {toolCount}
                  </Tag>
                ) : null}
                {msg.statusText ? (
                  <Text type="secondary" className={styles.metaText}>
                    {msg.statusText}
                  </Text>
                ) : null}
                {!isStreaming && metaParts.length > 0 ? (
                  <Text type="secondary" className={styles.metaText}>
                    {metaParts.join(' · ')}
                  </Text>
                ) : null}
                {!isStreaming && msg.assistantRunId ? (
                  <TraceDrawer msg={msg} />
                ) : null}
              </Space>
            );
          }

          // ToolCallTimeline 放在 footer 下方（通过 contentRender 追加）
          if (toolCount > 0 && !isWaiting) {
            const originalContentRender = item.contentRender || renderMarkdown;
            item.contentRender = (content: unknown) => (
              <>
                {originalContentRender(content)}
                <ToolCallTimeline toolCalls={msg.toolCalls} />
              </>
            );
          }
        }

        return item;
      }),
    [messages],
  );

  return (
    <div className={styles.container}>
      {loading && messages.length === 0 ? (
        <div className={styles.loadingTip}>正在加载会话消息…</div>
      ) : null}
      <Bubble.List
        className={styles.bubbleList}
        items={items}
        autoScroll
        role={{
          user: {
            placement: 'end',
            variant: 'filled',
            className: styles.bubbleUser,
          },
          ai: {
            placement: 'start',
            variant: 'filled',
            className: styles.bubbleAi,
          },
        }}
      />
    </div>
  );
};

export default ChatMessageList;
