import { useChatContext } from '@/contexts/ChatContext';
import { PlusOutlined, UserOutlined } from '@ant-design/icons';
import { useModel } from '@umijs/max';
import { Avatar, Button, Typography } from 'antd';
import React from 'react';
import styles from './index.module.less';

const { Text } = Typography;

const Sidebar: React.FC = () => {
  const {
    conversations,
    activeConversationId,
    setActiveConversationId,
    createNewConversation,
  } = useChatContext();

  const { initialState } = useModel('@@initialState');

  return (
    <div className={styles.sidebar}>
      <div className={styles.newChatWrapper}>
        <Button
          className={styles.newChatBtn}
          icon={<PlusOutlined />}
          onClick={createNewConversation}
          block
        >
          新对话
        </Button>
      </div>

      <div className={styles.divider} />

      <div className={styles.conversationList}>
        {conversations.length === 0 ? (
          <div className={styles.emptyTip}>
            <Text className={styles.emptyText}>暂无对话</Text>
          </div>
        ) : (
          conversations.map((conv) => (
            <div
              key={conv.id}
              className={`${styles.convItem} ${
                activeConversationId === conv.id ? styles.convItemActive : ''
              }`}
              onClick={() => setActiveConversationId(conv.id)}
            >
              <Text
                color="#fff"
                className={styles.convTitle}
                ellipsis={{ tooltip: conv.title || '新对话' }}
              >
                {conv.title || '新对话'}
              </Text>
            </div>
          ))
        )}
      </div>
      <div className={styles.divider} style={{ marginBottom: 0 }} />

      {/* User Info */}
      <div className={styles.userInfo}>
        <Avatar
          size={40}
          icon={<UserOutlined />}
          className={styles.userAvatar}
        />
        <Text className={styles.userName}>
          {initialState?.nickname || 'Loading...'}
        </Text>
      </div>
    </div>
  );
};

export default Sidebar;
