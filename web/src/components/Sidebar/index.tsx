import { useChatContext } from '@/contexts/ChatContext';
import { MessageOutlined, PlusOutlined } from '@ant-design/icons';
import { Badge, Button, Select, Typography } from 'antd';
import React from 'react';
import styles from './index.module.less';

const { Text } = Typography;

const Sidebar: React.FC = () => {
  const {
    health,
    healthError,
    models,
    currentModel,
    conversations,
    activeConversationId,
    conversationsLoading,
    conversationsError,
    createConversation,
    selectConversation,
    startNewConversation,
    handleSelectModel,
  } = useChatContext();

  const modelOptions =
    models?.available_models.map((m) => ({
      label: m,
      value: m,
    })) ?? [];

  return (
    <div className={styles.sidebar}>
      {/* 应用标题 */}
      <div className={styles.newChatWrapper}>
        <Text strong className={styles.appTitle}>
          My Python AI App
        </Text>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          className={styles.newChatBtn}
          block
          onClick={() => {
            startNewConversation();
            createConversation();
          }}
        >
          新建会话
        </Button>
      </div>

      <div className={styles.divider} />

      {/* 后端状态 */}
      <div className={styles.sectionPad}>
        {healthError ? (
          <Badge
            status="error"
            text={<Text className={styles.textDanger}>后端离线</Text>}
          />
        ) : health ? (
          <Badge
            status="success"
            text={<Text className={styles.textSuccess}>后端在线</Text>}
          />
        ) : (
          <Badge
            status="processing"
            text={<Text className={styles.textSm}>连接中…</Text>}
          />
        )}
      </div>

      {/* 模型选择 */}
      {modelOptions.length > 0 && (
        <div className={styles.sectionPad}>
          <Text className={styles.sectionLabel}>选择模型</Text>
          <Select
            className={styles.modelSelect}
            value={currentModel || undefined}
            options={modelOptions}
            onChange={handleSelectModel}
            placeholder="选择模型"
          />
        </div>
      )}

      <div className={styles.divider} />

      {/* 会话列表 */}
      <div className={styles.historyHeader}>
        <Text className={styles.sectionLabel}>会话</Text>
      </div>

      <div className={styles.conversationList}>
        {conversationsLoading ? (
          <div className={styles.emptyTip}>
            <Text className={styles.emptyText}>加载中…</Text>
          </div>
        ) : conversationsError ? (
          <div className={styles.emptyTip}>
            <Text className={styles.emptyText}>{conversationsError}</Text>
          </div>
        ) : conversations.length === 0 ? (
          <div className={styles.emptyTip}>
            <Text className={styles.emptyText}>暂无会话</Text>
          </div>
        ) : (
          conversations.map((item) => (
            <div
              key={item.id}
              className={`${styles.convItem} ${
                item.id === activeConversationId ? styles.convItemActive : ''
              }`}
              onClick={() => selectConversation(item.id)}
            >
              <MessageOutlined className={styles.convIcon} />
              <Text
                ellipsis={{ tooltip: item.title }}
                className={styles.convTitle}
              >
                {item.title}
              </Text>
              <Text className={styles.convMeta}>{item.message_count}</Text>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default Sidebar;
