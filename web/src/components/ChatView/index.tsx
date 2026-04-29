import { Typography } from 'antd';
import React from 'react';
import { useChatContext } from '../../contexts/ChatContext';
import ChatInputBar from '../ChatInputBar';
import ChatMessageList from '../ChatMessageList';
import styles from './index.module.less';

const { Text } = Typography;

const ChatView: React.FC = () => {
  const { messages, currentModel } = useChatContext();

  return (
    <div className={styles.chatView}>
      {/* Header */}
      <div className={styles.chatHeader}>
        <Text className={styles.chatTitle} ellipsis>
          {currentModel ? `当前模型：${currentModel}` : 'My Python AI App'}
        </Text>
      </div>

      {/* Messages */}
      <div className={styles.messagesArea}>
        <ChatMessageList messages={messages} />
      </div>

      {/* Input */}
      <ChatInputBar />
    </div>
  );
};

export default ChatView;
