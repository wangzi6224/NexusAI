import { ChatMessage } from '@/contexts/ChatContext';
import type {
  AssistantRunItem,
  ContextTrace,
  ContextTraceItem,
} from '@/services/api';
import { getAssistantRun } from '@/services/api';
import { InfoCircleOutlined } from '@ant-design/icons';
import {
  Button,
  Descriptions,
  Drawer,
  Empty,
  List,
  Space,
  Table,
  Tabs,
  Tag,
  Typography,
  message,
} from 'antd';
import type { ColumnsType } from 'antd/es/table';
import React, { useCallback, useState } from 'react';
import styles from './index.module.less';

const { Text, Paragraph } = Typography;

interface TraceDrawerProps {
  msg: ChatMessage;
}

type DroppedContextTraceItem = ContextTrace['dropped_items'][number] & {
  source?: string;
};

function isRecord(value: unknown): value is Record<string, unknown> {
  return value !== null && typeof value === 'object' && !Array.isArray(value);
}

function asContextTrace(value: unknown): ContextTrace | null {
  if (!isRecord(value)) return null;

  const selectedItems = Array.isArray(value.selected_items)
    ? (value.selected_items as ContextTraceItem[])
    : [];
  const droppedItems = Array.isArray(value.dropped_items)
    ? (value.dropped_items as ContextTrace['dropped_items'])
    : [];

  return {
    candidate_count:
      typeof value.candidate_count === 'number' ? value.candidate_count : 0,
    selected_count:
      typeof value.selected_count === 'number'
        ? value.selected_count
        : selectedItems.length,
    dropped_count:
      typeof value.dropped_count === 'number'
        ? value.dropped_count
        : droppedItems.length,
    total_estimated_tokens:
      typeof value.total_estimated_tokens === 'number'
        ? value.total_estimated_tokens
        : 0,
    max_context_tokens:
      typeof value.max_context_tokens === 'number'
        ? value.max_context_tokens
        : 0,
    selected_items: selectedItems,
    dropped_items: droppedItems,
    risk_flags: isRecord(value.risk_flags)
      ? {
          injection_risk:
            typeof value.risk_flags.injection_risk === 'boolean'
              ? value.risk_flags.injection_risk
              : undefined,
          matched_patterns: Array.isArray(value.risk_flags.matched_patterns)
            ? (value.risk_flags.matched_patterns as string[])
            : undefined,
        }
      : undefined,
  };
}

function getContextTrace(trace: Record<string, unknown>): ContextTrace | null {
  const nestedTrace = asContextTrace(trace.context);
  if (nestedTrace) return nestedTrace;

  return asContextTrace(trace);
}

function getRiskFlags(contextTrace: ContextTrace | null): {
  injection_risk: boolean;
  matched_patterns: string[];
} {
  const explicitPatterns = contextTrace?.risk_flags?.matched_patterns || [];
  const matchedPatterns = new Set<string>(explicitPatterns);
  let injectionRisk = Boolean(contextTrace?.risk_flags?.injection_risk);

  contextTrace?.selected_items.forEach((item) => {
    if (item.metadata?.injection_risk === true) {
      injectionRisk = true;
    }

    if (Array.isArray(item.metadata?.matched_patterns)) {
      item.metadata.matched_patterns.forEach((pattern) => {
        if (typeof pattern === 'string') {
          matchedPatterns.add(pattern);
        }
      });
    }
  });

  return {
    injection_risk: injectionRisk,
    matched_patterns: Array.from(matchedPatterns),
  };
}

const selectedColumns: ColumnsType<ContextTraceItem> = [
  {
    title: 'Type',
    dataIndex: 'type',
    key: 'type',
    width: 150,
    render: (value: string) => <Tag color="blue">{value}</Tag>,
  },
  {
    title: 'Source',
    dataIndex: 'source',
    key: 'source',
    width: 140,
  },
  {
    title: 'Placement',
    dataIndex: 'placement',
    key: 'placement',
    width: 110,
    render: (value: string) => <Tag>{value}</Tag>,
  },
  {
    title: 'Priority',
    dataIndex: 'priority',
    key: 'priority',
    width: 90,
  },
  {
    title: 'Score',
    dataIndex: 'score',
    key: 'score',
    width: 80,
    render: (value: number) =>
      typeof value === 'number' ? value.toFixed(3) : '-',
  },
  {
    title: 'Tokens',
    dataIndex: 'estimated_tokens',
    key: 'estimated_tokens',
    width: 90,
  },
  {
    title: 'Source ID',
    dataIndex: 'source_id',
    key: 'source_id',
    width: 180,
    render: (value?: string) =>
      value ? (
        <Text copyable code className={styles.idText}>
          {value}
        </Text>
      ) : (
        '-'
      ),
  },
];

const droppedColumns: ColumnsType<DroppedContextTraceItem> = [
  {
    title: 'Type',
    dataIndex: 'type',
    key: 'type',
    width: 160,
    render: (value: string) => <Tag color="default">{value}</Tag>,
  },
  {
    title: 'Source',
    dataIndex: 'source',
    key: 'source',
    width: 140,
    render: (value?: string) => value || '-',
  },
  {
    title: 'Reason',
    dataIndex: 'reason',
    key: 'reason',
    width: 140,
    render: (value: string) => <Tag color="orange">{value}</Tag>,
  },
  {
    title: 'Detail',
    dataIndex: 'detail',
    key: 'detail',
    render: (value?: string) => value || '-',
  },
];

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
  const contextTrace = getContextTrace(trace);
  const riskFlags = getRiskFlags(contextTrace);
  const selectedItems = contextTrace?.selected_items || [];
  const droppedItems = (contextTrace?.dropped_items ||
    []) as DroppedContextTraceItem[];

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
        className={styles.drawer}
        open={open}
        onClose={() => setOpen(false)}
        width={1200}
        loading={loading}
      >
        <Tabs
          items={[
            {
              key: 'overview',
              label: 'Overview',
              children: (
                <>
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
                        <Tag
                          color={
                            resolvedMode === 'agent' ? 'processing' : 'cyan'
                          }
                        >
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
                        <Text>
                          {runDetail?.latency_ms || msg.latency_ms} ms
                        </Text>
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
                                  ellipsis={{
                                    rows: 2,
                                    expandable: true,
                                    symbol: '展开',
                                  }}
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
                </>
              ),
            },
            {
              key: 'context',
              label: 'Context',
              children: contextTrace ? (
                <>
                  <div className={styles.section}>
                    <Text strong className={styles.sectionTitle}>
                      Summary
                    </Text>
                    <Descriptions column={2} size="small" bordered>
                      <Descriptions.Item label="total_estimated_tokens">
                        {contextTrace.total_estimated_tokens}
                      </Descriptions.Item>
                      <Descriptions.Item label="max_context_tokens">
                        {contextTrace.max_context_tokens}
                      </Descriptions.Item>
                      <Descriptions.Item label="selected_count">
                        {contextTrace.selected_count}
                      </Descriptions.Item>
                      <Descriptions.Item label="dropped_count">
                        {contextTrace.dropped_count}
                      </Descriptions.Item>
                    </Descriptions>
                  </div>

                  <div className={styles.section}>
                    <Text strong className={styles.sectionTitle}>
                      Selected Items ({selectedItems.length})
                    </Text>
                    <Table
                      size="small"
                      rowKey="id"
                      columns={selectedColumns}
                      dataSource={selectedItems}
                      pagination={false}
                      scroll={{ x: 880 }}
                    />
                  </div>

                  <div className={styles.section}>
                    <Text strong className={styles.sectionTitle}>
                      Dropped Items ({droppedItems.length})
                    </Text>
                    <Table
                      size="small"
                      rowKey="id"
                      columns={droppedColumns}
                      dataSource={droppedItems}
                      pagination={false}
                      scroll={{ x: 620 }}
                    />
                  </div>

                  <div className={styles.section}>
                    <Text strong className={styles.sectionTitle}>
                      Risk Flags
                    </Text>
                    <Descriptions column={1} size="small" bordered>
                      <Descriptions.Item label="injection_risk">
                        <Tag
                          color={riskFlags.injection_risk ? 'error' : 'green'}
                        >
                          {riskFlags.injection_risk ? 'true' : 'false'}
                        </Tag>
                      </Descriptions.Item>
                      <Descriptions.Item label="matched_patterns">
                        {riskFlags.matched_patterns.length > 0 ? (
                          <Space size={[4, 4]} wrap>
                            {riskFlags.matched_patterns.map((pattern) => (
                              <Tag key={pattern} color="red">
                                {pattern}
                              </Tag>
                            ))}
                          </Space>
                        ) : (
                          <Text type="secondary">-</Text>
                        )}
                      </Descriptions.Item>
                    </Descriptions>
                  </div>
                </>
              ) : (
                <Empty
                  image={Empty.PRESENTED_IMAGE_SIMPLE}
                  description="暂无 Context Trace"
                />
              ),
            },
            {
              key: 'json',
              label: 'Trace JSON',
              children:
                Object.keys(trace).length > 0 ? (
                  <Text code className={styles.traceJson}>
                    {JSON.stringify(trace, null, 2)}
                  </Text>
                ) : (
                  <Empty
                    image={Empty.PRESENTED_IMAGE_SIMPLE}
                    description="暂无 Trace JSON"
                  />
                ),
            },
          ]}
        />
      </Drawer>
    </>
  );
};

export default TraceDrawer;
