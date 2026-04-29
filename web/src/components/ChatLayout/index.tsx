import React from 'react';
import { useChatContext } from '../../contexts/ChatContext';
import ChatView from '../ChatView';
import Sidebar from '../Sidebar';
import WelcomeScreen from '../WelcomeScreen';
import styles from './index.module.less';

const ChatLayout: React.FC = () => {
  const { messages } = useChatContext();

  return (
    <div className={styles.appLayout}>
      {/* Left Sidebar */}
      <Sidebar />

      {/* Main Content */}
      <div className={styles.mainArea}>
        {messages.length > 0 ? <ChatView /> : <WelcomeScreen />}
      </div>
    </div>
  );
};

export default ChatLayout;
