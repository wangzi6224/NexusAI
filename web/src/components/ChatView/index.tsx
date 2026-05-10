import { Typography } from 'antd';
import React from 'react';
import { useChatContext } from '../../contexts/ChatContext';
import ChatInputBar from '../ChatInputBar';
import ChatMessageList from '../ChatMessageList';
import styles from './index.module.less';

const { Text } = Typography;

const ChatView: React.FC = () => {
  const { messages, currentModel, activeConversation, messagesLoading } =
    useChatContext();

  return (
    <div className={styles.chatView}>
      {/* Header */}
      <div className={styles.chatHeader}>
        <Text className={styles.chatTitle} ellipsis>
          {activeConversation?.title || '新会话'}
          {currentModel ? ` · ${currentModel}` : ''}
        </Text>
      </div>

      {/* Messages */}
      <div className={styles.messagesArea}>
        <ChatMessageList messages={messages} loading={messagesLoading} />
      </div>

      {/* Input */}
      <ChatInputBar />
    </div>
  );
};

export default ChatView;
