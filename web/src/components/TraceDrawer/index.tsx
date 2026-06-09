import { ChatMessage } from '@/contexts/ChatContext';
import type {
  AssistantRunItem,
  AssistantToolCallEvent,
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

type McpTrace = {
  enabled: boolean;
  used: boolean;
  server_list: string[];
  allowed_tools: string[];
  tool_calls: AssistantToolCallEvent[];
  audit_ids: string[];
  permission_denied_records: Array<Record<string, unknown>>;
};

function isRecord(value: unknown): value is Record<string, unknown> {
  return value !== null && typeof value === 'object' && !Array.isArray(value);
}

function stringArray(value: unknown): string[] {
  return Array.isArray(value)
    ? value.filter((item): item is string => typeof item === 'string')
    : [];
}

function getNestedString(
  value: Record<string, unknown> | undefined,
  path: string[],
): string | undefined {
  let current: unknown = value;

  for (const key of path) {
    if (!current || typeof current !== 'object' || Array.isArray(current)) {
      return undefined;
    }

    current = (current as Record<string, unknown>)[key];
  }

  return typeof current === 'string' ? current : undefined;
}

function inferMcpServerName(toolName?: string): string | undefined {
  if (!toolName?.startsWith('mcp__')) return undefined;

  const [, serverName] = toolName.split('__');
  return serverName || undefined;
}

function getToolSource(tc: AssistantToolCallEvent): string {
  return (
    tc.source ||
    getNestedString(tc.result, ['metadata', 'source']) ||
    (tc.tool_name?.startsWith('mcp__') ? 'mcp' : 'internal')
  );
}

function getServerName(tc: AssistantToolCallEvent): string | undefined {
  return (
    tc.server_name ||
    getNestedString(tc.result, ['metadata', 'server_name']) ||
    getNestedString(tc.result, ['data', 'server_name']) ||
    inferMcpServerName(tc.tool_name)
  );
}

function getRiskLevel(tc: AssistantToolCallEvent): string {
  return (
    tc.risk_level ||
    getNestedString(tc.result, ['metadata', 'risk_level']) ||
    'low'
  );
}

function getToolStatus(tc: AssistantToolCallEvent): string {
  if (tc.error_code === 'MCP_PERMISSION_DENIED') return 'denied';
  if (tc.success === undefined) return 'running';
  return tc.success ? 'success' : 'failed';
}

function getStatusColor(status: string): string {
  if (status === 'success') return 'success';
  if (status === 'denied') return 'warning';
  if (status === 'failed') return 'error';
  return 'processing';
}

function getRiskColor(riskLevel: string): string {
  if (riskLevel === 'high') return 'error';
  if (riskLevel === 'medium') return 'warning';
  return 'success';
}

function asMcpTrace(
  value: unknown,
  fallbackToolCalls: AssistantToolCallEvent[],
): McpTrace {
  const trace = isRecord(value) ? value : {};
  const traceToolCalls = Array.isArray(trace.tool_calls)
    ? (trace.tool_calls as AssistantToolCallEvent[])
    : [];
  const toolCalls =
    traceToolCalls.length > 0
      ? traceToolCalls
      : fallbackToolCalls.filter((item) => getToolSource(item) === 'mcp');
  const permissionDeniedRecords = Array.isArray(
    trace.permission_denied_records,
  )
    ? (trace.permission_denied_records as Array<Record<string, unknown>>)
    : toolCalls
        .filter((item) => getToolStatus(item) === 'denied')
        .map((item) => item as Record<string, unknown>);

  return {
    enabled:
      typeof trace.enabled === 'boolean' ? trace.enabled : toolCalls.length > 0,
    used: typeof trace.used === 'boolean' ? trace.used : toolCalls.length > 0,
    server_list:
      stringArray(trace.server_list).length > 0
        ? stringArray(trace.server_list)
        : stringArray(trace.servers),
    allowed_tools: stringArray(trace.allowed_tools),
    tool_calls: toolCalls,
    audit_ids: stringArray(trace.audit_ids),
    permission_denied_records: permissionDeniedRecords,
  };
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

const mcpToolColumns: ColumnsType<AssistantToolCallEvent> = [
  {
    title: 'Tool',
    dataIndex: 'tool_name',
    key: 'tool_name',
    width: 240,
    render: (value?: string) =>
      value ? (
        <Text code className={styles.idText}>
          {value}
        </Text>
      ) : (
        '-'
      ),
  },
  {
    title: 'Source',
    key: 'source',
    width: 100,
    render: (_, record) => <Tag color="purple">{getToolSource(record)}</Tag>,
  },
  {
    title: 'Server',
    key: 'server_name',
    width: 150,
    render: (_, record) => getServerName(record) || '-',
  },
  {
    title: 'Risk',
    key: 'risk_level',
    width: 100,
    render: (_, record) => {
      const riskLevel = getRiskLevel(record);
      return <Tag color={getRiskColor(riskLevel)}>{riskLevel}</Tag>;
    },
  },
  {
    title: 'Status',
    key: 'status',
    width: 110,
    render: (_, record) => {
      const status = getToolStatus(record);
      return <Tag color={getStatusColor(status)}>{status}</Tag>;
    },
  },
  {
    title: 'Latency',
    dataIndex: 'latency_ms',
    key: 'latency_ms',
    width: 100,
    render: (value?: number) =>
      typeof value === 'number' ? `${value}ms` : '-',
  },
  {
    title: 'Error',
    key: 'error',
    render: (_, record) =>
      record.error_message ? (
        <Text type="danger">
          {record.error_code ? `[${record.error_code}] ` : ''}
          {record.error_message}
        </Text>
      ) : (
        '-'
      ),
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
  const mcpTrace = asMcpTrace(trace.mcp, toolCalls);

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
                            resolvedMode === 'agent'
                              ? 'processing'
                              : resolvedMode === 'mcp'
                              ? 'purple'
                              : 'cyan'
                          }
                        >
                          {resolvedMode === 'agent'
                            ? 'Agent'
                            : resolvedMode === 'mcp'
                            ? 'MCP 外部工具'
                            : '普通'}
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
              key: 'mcp',
              label: 'MCP',
              children: (
                <>
                  <div className={styles.section}>
                    <Text strong className={styles.sectionTitle}>
                      Summary
                    </Text>
                    <Descriptions column={2} size="small" bordered>
                      <Descriptions.Item label="enabled">
                        <Tag color={mcpTrace.enabled ? 'success' : 'default'}>
                          {String(mcpTrace.enabled)}
                        </Tag>
                      </Descriptions.Item>
                      <Descriptions.Item label="used">
                        <Tag color={mcpTrace.used ? 'processing' : 'default'}>
                          {String(mcpTrace.used)}
                        </Tag>
                      </Descriptions.Item>
                      <Descriptions.Item label="server list">
                        {mcpTrace.server_list.length > 0 ? (
                          <Space size={[4, 4]} wrap>
                            {mcpTrace.server_list.map((server) => (
                              <Tag key={server} color="geekblue">
                                {server}
                              </Tag>
                            ))}
                          </Space>
                        ) : (
                          <Text type="secondary">-</Text>
                        )}
                      </Descriptions.Item>
                      <Descriptions.Item label="allowed tools">
                        {mcpTrace.allowed_tools.length > 0 ? (
                          <Space size={[4, 4]} wrap>
                            {mcpTrace.allowed_tools.map((tool) => (
                              <Tag key={tool} color="blue">
                                {tool}
                              </Tag>
                            ))}
                          </Space>
                        ) : (
                          <Text type="secondary">-</Text>
                        )}
                      </Descriptions.Item>
                      <Descriptions.Item label="audit ids">
                        {mcpTrace.audit_ids.length > 0 ? (
                          <Space direction="vertical" size={2}>
                            {mcpTrace.audit_ids.map((auditId) => (
                              <Text
                                key={auditId}
                                copyable
                                code
                                className={styles.idText}
                              >
                                {auditId}
                              </Text>
                            ))}
                          </Space>
                        ) : (
                          <Text type="secondary">-</Text>
                        )}
                      </Descriptions.Item>
                    </Descriptions>
                  </div>

                  <div className={styles.section}>
                    <Text strong className={styles.sectionTitle}>
                      Tool Calls ({mcpTrace.tool_calls.length})
                    </Text>
                    {mcpTrace.tool_calls.length > 0 ? (
                      <Table
                        size="small"
                        rowKey={(record, index) =>
                          `${record.tool_name || 'mcp-tool'}-${
                            record.step ?? index
                          }`
                        }
                        columns={mcpToolColumns}
                        dataSource={mcpTrace.tool_calls}
                        pagination={false}
                        scroll={{ x: 920 }}
                      />
                    ) : (
                      <Empty
                        image={Empty.PRESENTED_IMAGE_SIMPLE}
                        description="暂无 MCP 工具调用"
                      />
                    )}
                  </div>

                  <div className={styles.section}>
                    <Text strong className={styles.sectionTitle}>
                      Permission Denied Records (
                      {mcpTrace.permission_denied_records.length})
                    </Text>
                    {mcpTrace.permission_denied_records.length > 0 ? (
                      <List
                        size="small"
                        dataSource={mcpTrace.permission_denied_records}
                        renderItem={(record, idx) => (
                          <List.Item key={idx} className={styles.listItem}>
                            <Text code className={styles.traceJsonInline}>
                              {JSON.stringify(record, null, 2)}
                            </Text>
                          </List.Item>
                        )}
                      />
                    ) : (
                      <Empty
                        image={Empty.PRESENTED_IMAGE_SIMPLE}
                        description="暂无权限拒绝记录"
                      />
                    )}
                  </div>
                </>
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
