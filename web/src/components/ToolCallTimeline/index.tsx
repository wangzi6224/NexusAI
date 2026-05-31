import { AssistantToolCallEvent } from '@/services/api';
import {
  CheckCircleOutlined,
  CloseCircleOutlined,
  LoadingOutlined,
  ToolOutlined,
} from '@ant-design/icons';
import { Collapse, Tag, Timeline, Typography } from 'antd';
import React from 'react';
import styles from './index.module.less';

const { Text } = Typography;

interface ToolCallTimelineProps {
  toolCalls?: AssistantToolCallEvent[];
}

const ToolCallTimeline: React.FC<ToolCallTimelineProps> = ({ toolCalls }) => {
  if (!toolCalls || toolCalls.length === 0) return null;

  const items = toolCalls.map((tc, idx) => {
    const key = `${tc.tool_name ?? 'tool'}-${tc.step ?? idx}`;

    // 状态图标
    let dot: React.ReactNode;
    if (tc.success === undefined) {
      dot = <LoadingOutlined />;
    } else if (tc.success) {
      dot = <CheckCircleOutlined style={{ color: '#52c41a' }} />;
    } else {
      dot = <CloseCircleOutlined style={{ color: '#ff4d4f' }} />;
    }

    // arguments 折叠内容
    const hasArgs = tc.arguments && Object.keys(tc.arguments).length > 0;
    const argPanel = hasArgs
      ? [
          {
            key: 'args',
            label: '参数',
            children: (
              <Text code className={styles.argCode}>
                {JSON.stringify(tc.arguments, null, 2)}
              </Text>
            ),
          },
        ]
      : undefined;

    return {
      key,
      dot,
      children: (
        <div className={styles.item}>
          <div className={styles.itemHeader}>
            <ToolOutlined className={styles.toolIcon} />
            <Text strong className={styles.toolName}>
              {tc.tool_name || '未知工具'}
            </Text>
            {tc.step !== undefined && (
              <Tag color="default" className={styles.stepTag}>
                Step {tc.step}
              </Tag>
            )}
            {tc.latency_ms !== undefined && (
              <Text type="secondary" className={styles.latency}>
                {tc.latency_ms} ms
              </Text>
            )}
          </div>
          {tc.reason && (
            <Text type="secondary" className={styles.reason}>
              {tc.reason}
            </Text>
          )}
          {tc.success === false && tc.error_message && (
            <Text type="danger" className={styles.error}>
              {tc.error_code ? `[${tc.error_code}] ` : ''}
              {tc.error_message}
            </Text>
          )}
          {argPanel && (
            <Collapse
              size="small"
              ghost
              items={argPanel}
              className={styles.argsCollapse}
            />
          )}
        </div>
      ),
    };
  });

  return (
    <div className={styles.container}>
      <Text type="secondary" className={styles.title}>
        工具调用
      </Text>
      <Timeline items={items} className={styles.timeline} />
    </div>
  );
};

export default ToolCallTimeline;
