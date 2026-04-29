import { Typography } from 'antd';
import React from 'react';
import ChatSenderInput from '../ChatSenderInput';
import styles from './index.module.less';

const { Text } = Typography;

const ChatInputBar: React.FC = () => {
  return (
    <div className={styles.container}>
      <ChatSenderInput autoSize={{ minRows: 2, maxRows: 6 }} />
      <div className={styles.disclaimer}>
        <Text className={styles.disclaimerText}>内容由AI生成，请仔细甄别</Text>
      </div>
    </div>
  );
};

export default ChatInputBar;
