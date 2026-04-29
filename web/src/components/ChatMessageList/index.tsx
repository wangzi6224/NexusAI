import { ChatMessage } from '@/contexts/ChatContext';
import type { BubbleProps } from '@ant-design/x';
import { Bubble } from '@ant-design/x';
import { XMarkdown } from '@ant-design/x-markdown';
import React, { useMemo } from 'react';
import FeedbackFooter from '../FeedbackFooter';
import styles from './index.module.less';

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
          // 流式和完成态都用 Markdown 渲染，实现实时推流实时展示
          item.contentRender = renderMarkdown;
          item.streaming = msg.streaming ?? false;

          if (!msg.streaming) {
            item.footer = (
              <FeedbackFooter messageId={msg.messageId} helpful={msg.helpful} />
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
