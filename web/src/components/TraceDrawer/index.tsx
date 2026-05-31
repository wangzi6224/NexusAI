import { ChatMessage } from '@/contexts/ChatContext';
import { AssistantRunItem, getAssistantRun } from '@/services/api';
import { InfoCircleOutlined } from '@ant-design/icons';
import {
  Button,
  Descriptions,
  Drawer,
  List,
  Tag,
  Typography,
  message,
} from 'antd';
import React, { useCallback, useState } from 'react';
import styles from './index.module.less';

const { Text, Paragraph } = Typography;

interface TraceDrawerProps {
  msg: ChatMessage;
}

const TraceDrawer: React.FC<TraceDrawerProps> = ({ msg }) => {
  const [open, setOpen] = useState(false);
  const [runDetail, setRunDetail] = useState<AssistantRunItem | null>(null);
  const [loading, setLoading] = useState(false);

  const handleOpen = useCallback(async () => {
    setOpen(true);
    // 如果有 assistantRunId，尝试从后端拉取最新详情
    if (msg.assistantRunId && !runDetail) {
      setLoading(true);
      try {
        const data = await getAssistantRun(msg.assistantRunId);
        setRunDetail(data);
      } catch (err: any) {
        message.error(
          err?.response?.data?.detail ||
            err?.message ||
            '获取 AssistantRun 失败',
        );
      } finally {
        setLoading(false);
      }
    }
  }, [msg.assistantRunId, runDetail]);

  if (!msg.assistantRunId) return null;

  const resolvedMode = runDetail?.mode || msg.resolvedMode;
  const toolCalls = msg.toolCalls || [];
  const sources = msg.sources || [];
  const trace = runDetail?.trace || msg.trace || {};

  return (
    <>
      <Button
        type="link"
        size="small"
        icon={<InfoCircleOutlined />}
        className={styles.traceBtn}
        onClick={handleOpen}
      >
        查看 Trace
      </Button>

      <Drawer
        title="Assistant Trace"
        open={open}
        onClose={() => setOpen(false)}
        width={520}
        loading={loading}
        destroyOnClose={false}
      >
        <Descriptions
          column={1}
          size="small"
          bordered
          className={styles.descriptions}
        >
          <Descriptions.Item label="Assistant Run ID">
            <Text copyable code className={styles.idText}>
              {msg.assistantRunId}
            </Text>
          </Descriptions.Item>
          {(runDetail?.agent_run_id || msg.agentRunId) && (
            <Descriptions.Item label="Agent Run ID">
              <Text copyable code className={styles.idText}>
                {runDetail?.agent_run_id || msg.agentRunId}
              </Text>
            </Descriptions.Item>
          )}
          {resolvedMode && (
            <Descriptions.Item label="Mode">
              <Tag color={resolvedMode === 'agent' ? 'processing' : 'cyan'}>
                {resolvedMode === 'agent' ? 'Agent' : '聊天'}
              </Tag>
            </Descriptions.Item>
          )}
          {msg.routeReason && (
            <Descriptions.Item label="路由原因">
              <Text>{msg.routeReason}</Text>
            </Descriptions.Item>
          )}
          {msg.matchedKeywords && msg.matchedKeywords.length > 0 && (
            <Descriptions.Item label="匹配关键词">
              {msg.matchedKeywords.map((kw) => (
                <Tag key={kw} color="orange">
                  {kw}
                </Tag>
              ))}
            </Descriptions.Item>
          )}
          {(runDetail?.latency_ms || msg.latency_ms) && (
            <Descriptions.Item label="耗时">
              <Text>{runDetail?.latency_ms || msg.latency_ms} ms</Text>
            </Descriptions.Item>
          )}
          {(runDetail?.model || msg.model) && (
            <Descriptions.Item label="模型">
              <Text>{runDetail?.model || msg.model}</Text>
            </Descriptions.Item>
          )}
          {(runDetail?.provider || msg.provider) && (
            <Descriptions.Item label="Provider">
              <Text>{runDetail?.provider || msg.provider}</Text>
            </Descriptions.Item>
          )}
        </Descriptions>

        {toolCalls.length > 0 && (
          <div className={styles.section}>
            <Text strong className={styles.sectionTitle}>
              工具调用 ({toolCalls.length})
            </Text>
            <List
              size="small"
              dataSource={toolCalls}
              renderItem={(tc, idx) => (
                <List.Item key={idx} className={styles.listItem}>
                  <div>
                    <Text strong>{tc.tool_name || '未知工具'}</Text>
                    {tc.step !== undefined && (
                      <Tag color="default" style={{ marginLeft: 6 }}>
                        Step {tc.step}
                      </Tag>
                    )}
                    {tc.success !== undefined && (
                      <Tag
                        color={tc.success ? 'success' : 'error'}
                        style={{ marginLeft: 4 }}
                      >
                        {tc.success ? '成功' : '失败'}
                      </Tag>
                    )}
                    {tc.latency_ms !== undefined && (
                      <Text
                        type="secondary"
                        style={{ marginLeft: 6, fontSize: 11 }}
                      >
                        {tc.latency_ms} ms
                      </Text>
                    )}
                    {tc.reason && (
                      <Paragraph
                        type="secondary"
                        style={{ margin: 0, fontSize: 12 }}
                      >
                        {tc.reason}
                      </Paragraph>
                    )}
                    {tc.error_message && (
                      <Paragraph
                        type="danger"
                        style={{ margin: 0, fontSize: 12 }}
                      >
                        {tc.error_message}
                      </Paragraph>
                    )}
                  </div>
                </List.Item>
              )}
            />
          </div>
        )}

        {sources.length > 0 && (
          <div className={styles.section}>
            <Text strong className={styles.sectionTitle}>
              引用来源 ({sources.length})
            </Text>
            <List
              size="small"
              dataSource={sources}
              renderItem={(src, idx) => (
                <List.Item
                  key={src.chunk_id || idx}
                  className={styles.listItem}
                >
                  <div>
                    <Text strong>{src.filename || '未知文件'}</Text>
                    {src.chunk_index !== undefined && (
                      <Tag color="default" style={{ marginLeft: 6 }}>
                        Chunk #{src.chunk_index}
                      </Tag>
                    )}
                    {src.score !== undefined && (
                      <Tag color="blue" style={{ marginLeft: 4 }}>
                        {src.score.toFixed(3)}
                      </Tag>
                    )}
                    {src.heading && (
                      <Paragraph
                        type="secondary"
                        style={{ margin: 0, fontSize: 12 }}
                      >
                        {src.heading}
                      </Paragraph>
                    )}
                    {src.content_preview && (
                      <Paragraph
                        type="secondary"
                        style={{ margin: 0, fontSize: 12 }}
                        ellipsis={{ rows: 2, expandable: true, symbol: '展开' }}
                      >
                        {src.content_preview}
                      </Paragraph>
                    )}
                  </div>
                </List.Item>
              )}
            />
          </div>
        )}

        {Object.keys(trace).length > 0 && (
          <div className={styles.section}>
            <Text strong className={styles.sectionTitle}>
              Trace JSON
            </Text>
            <Text code className={styles.traceJson}>
              {JSON.stringify(trace, null, 2)}
            </Text>
          </div>
        )}
      </Drawer>
    </>
  );
};

export default TraceDrawer;
