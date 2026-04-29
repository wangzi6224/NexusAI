import { ChatMessage } from '@/contexts/ChatContext';
import type { BubbleProps } from '@ant-design/x';
import { Bubble } from '@ant-design/x';
import { XMarkdown } from '@ant-design/x-markdown';
import { Typography } from 'antd';
import React, { useMemo } from 'react';
import styles from './index.module.less';

const { Text } = Typography;

interface ChatMessageListProps {
  messages: ChatMessage[];
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

const ChatMessageList: React.FC<ChatMessageListProps> = ({ messages }) => {
  const items = useMemo(
    () =>
      messages.map((msg): BubbleItem => {
        const item: BubbleItem = {
          key: msg.id,
          role: msg.role,
          content: msg.content,
          loading: msg.loading,
        };

        if (msg.role === 'ai' && !msg.loading) {
          item.contentRender = renderMarkdown;

          // 显示元信息：provider/model/latency/tokens
          const metaParts: string[] = [];
          if (msg.model) metaParts.push(msg.model);
          if (msg.provider) metaParts.push(msg.provider);
          if (msg.latency_ms != null) metaParts.push(`${msg.latency_ms} ms`);
          if (msg.usage?.total_tokens != null)
            metaParts.push(`${msg.usage.total_tokens} tokens`);

          if (metaParts.length > 0) {
            item.footer = (
              <Text type="secondary" className={styles.metaText}>
                {metaParts.join(' · ')}
              </Text>
            );
          }
        }

        return item;
      }),
    [messages],
  );

  return (
    <div className={styles.container}>
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
