import { useChatContext } from '@/contexts/ChatContext';
import { ClearOutlined } from '@ant-design/icons';
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
    history,
    historyLoading,
    doClearHistory,
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
            size="small"
            value={currentModel || undefined}
            options={modelOptions}
            onChange={handleSelectModel}
            placeholder="选择模型"
          />
        </div>
      )}

      <div className={styles.divider} />

      {/* 历史记录标题 + 清空按钮 */}
      <div className={styles.historyHeader}>
        <Text className={styles.sectionLabel}>历史记录</Text>
        <Button
          type="text"
          size="small"
          icon={<ClearOutlined />}
          className={styles.clearBtn}
          onClick={doClearHistory}
        >
          清空
        </Button>
      </div>

      <div className={styles.conversationList}>
        {historyLoading ? (
          <div className={styles.emptyTip}>
            <Text className={styles.emptyText}>加载中…</Text>
          </div>
        ) : history.length === 0 ? (
          <div className={styles.emptyTip}>
            <Text className={styles.emptyText}>暂无历史记录</Text>
          </div>
        ) : (
          history.map((item, idx) => (
            <div key={idx} className={styles.convItem}>
              <Text
                className={styles.convTitle}
                ellipsis={{ tooltip: item.content }}
                style={{
                  color: item.role === 'user' ? '#fff' : '#bbb',
                  fontSize: 12,
                }}
              >
                {item.role === 'user' ? '你：' : 'AI：'}
                {item.content}
              </Text>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default Sidebar;
