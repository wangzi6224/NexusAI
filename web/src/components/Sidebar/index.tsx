import { useChatContext } from '@/contexts/ChatContext';
import {
  DeleteOutlined,
  MessageOutlined,
  PlusOutlined,
} from '@ant-design/icons';
import { Badge, Button, Popconfirm, Select, Typography } from 'antd';
import React from 'react';
import styles from './index.module.less';

const { Text } = Typography;

const Sidebar: React.FC = () => {
  const {
    health,
    healthError,
    models,
    currentProvider,
    currentModel,
    conversations,
    activeConversationId,
    conversationsLoading,
    conversationsError,
    createConversation,
    deleteConversation,
    selectConversation,
    startNewConversation,
    handleSelectProvider,
    handleSelectModel,
  } = useChatContext();

  const providerOptions =
    models?.providers?.map((item) => ({
      label: item.provider,
      value: item.provider,
    })) ?? [];

  const selectedProviderModels = models?.providers?.find(
    (item) => item.provider === currentProvider,
  );

  const modelOptions = (
    selectedProviderModels?.available_models ||
    models?.available_models ||
    []
  ).map((m) => ({
    label: m,
    value: m,
  }));

  return (
    <div className={styles.sidebar}>
      {/* 应用标题 */}
      <div className={styles.newChatWrapper}>
        <Text strong className={styles.appTitle}>
          NexusAI
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

      {/* Provider / 模型选择 */}
      {providerOptions.length > 0 && (
        <div className={styles.sectionPad}>
          <Text className={styles.sectionLabel}>选择 Provider</Text>
          <Select
            className={styles.modelSelect}
            value={currentProvider || undefined}
            options={providerOptions}
            onChange={handleSelectProvider}
            placeholder="选择 Provider"
          />
        </div>
      )}

      {modelOptions.length > 0 && (
        <div className={styles.sectionPad}>
          <Text className={styles.sectionLabel}>选择模型</Text>
          <Select
            className={styles.modelSelect}
            value={currentModel || undefined}
            options={modelOptions}
            onChange={(model) => handleSelectModel(model, currentProvider)}
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
              <Popconfirm
                title="删除会话"
                description="确定要删除该会话及其全部消息吗？"
                onConfirm={(e) => {
                  e?.stopPropagation();
                  deleteConversation(item.id);
                }}
                onCancel={(e) => {
                  e?.stopPropagation();
                }}
                okText="确定"
                cancelText="取消"
                placement="right"
              >
                <DeleteOutlined
                  className={styles.convDeleteBtn}
                  onClick={(e) => e.stopPropagation()}
                />
              </Popconfirm>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default Sidebar;
