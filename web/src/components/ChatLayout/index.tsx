import React from 'react';
import { useChatContext } from '../../contexts/ChatContext';
import ChatView from '../ChatView';
import Sidebar from '../Sidebar';
import WelcomeScreen from '../WelcomeScreen';
import styles from './index.module.less';

const ChatLayout: React.FC = () => {
  const { activeConversation } = useChatContext();

  return (
    <div className={styles.appLayout}>
      {/* Left Sidebar */}
      <Sidebar />

      {/* Main Content */}
      <div className={styles.mainArea}>
        {activeConversation ? <ChatView /> : <WelcomeScreen />}
      </div>
    </div>
  );
};

export default ChatLayout;
