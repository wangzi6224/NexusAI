import {
  AgentRunItem,
  ConversationItem,
  getAgentRuns,
  getConversations,
} from '@/services';
import { EyeOutlined, ReloadOutlined } from '@ant-design/icons';
import { history, useLocation } from '@umijs/max';
import {
  Alert,
  Button,
  Card,
  Empty,
  Select,
  Space,
  Table,
  Tag,
  Typography,
} from 'antd';
import type { ColumnsType } from 'antd/es/table';
import axios from 'axios';
import React, { useEffect, useMemo, useState } from 'react';
import styles from './index.module.less';

const { Paragraph, Text, Title } = Typography;

const getErrorText = (error: unknown): string => {
  if (axios.isAxiosError(error)) {
    const data = error.response?.data as
      | { message?: string; detail?: unknown; code?: string }
      | undefined;
    const detailText =
      typeof data?.detail === 'string' ? data.detail : undefined;

    return (
      data?.message ||
      detailText ||
      data?.code ||
      error.message ||
      '请求失败，请稍后重试'
    );
  }

  if (error instanceof Error) return error.message;

  return '请求失败，请稍后重试';
};

const formatDateTime = (value?: string): string => {
  if (!value) return '-';

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) return value;

  return date.toLocaleString('zh-CN', { hour12: false });
};

const formatLatency = (value?: number | null): string => {
  if (typeof value !== 'number' || Number.isNaN(value)) return '-';

  return `${value}ms`;
};

const statusColor = (status?: string): string => {
  const normalized = (status || '').toLowerCase();

  if (normalized.includes('fail') || normalized.includes('error')) {
    return 'error';
  }

  if (normalized.includes('run') || normalized.includes('pending')) {
    return 'processing';
  }

  if (
    normalized.includes('done') ||
    normalized.includes('complete') ||
    normalized.includes('success')
  ) {
    return 'success';
  }

  return 'default';
};

const getConversationLabel = (item: ConversationItem): string => {
  const title = item.title || item.id;
  const suffix = item.message_count ? ` · ${item.message_count} 条消息` : '';

  return `${title}${suffix}`;
};

const AgentTracePage: React.FC = () => {
  const location = useLocation();
  const [conversations, setConversations] = useState<ConversationItem[]>([]);
  const [selectedConversationId, setSelectedConversationId] =
    useState<string>('');
  const [conversationLoading, setConversationLoading] =
    useState<boolean>(false);
  const [runs, setRuns] = useState<AgentRunItem[]>([]);
  const [runsLoading, setRunsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string>('');

  const queryConversationId = useMemo(() => {
    return new URLSearchParams(location.search).get('conversation_id') || '';
  }, [location.search]);

  const conversationOptions = useMemo(
    () =>
      conversations.map((item) => ({
        label: getConversationLabel(item),
        value: item.id,
      })),
    [conversations],
  );

  const fetchRuns = async (conversationId: string): Promise<void> => {
    if (!conversationId) {
      setRuns([]);
      return;
    }

    setRunsLoading(true);
    setError('');

    try {
      const response = await getAgentRuns(conversationId);
      setRuns(response.runs || []);
    } catch (requestError) {
      setRuns([]);
      setError(getErrorText(requestError));
    } finally {
      setRunsLoading(false);
    }
  };

  const syncSelectedConversation = (conversationId: string): void => {
    setSelectedConversationId(conversationId);

    if (conversationId) {
      history.replace(
        `/traces?conversation_id=${encodeURIComponent(conversationId)}`,
      );
    } else {
      history.replace('/traces');
    }
  };

  const fetchConversations = async (): Promise<void> => {
    setConversationLoading(true);
    setError('');

    try {
      const response = await getConversations();
      const items = response.items || [];
      setConversations(items);

      const nextConversationId =
        queryConversationId && items.some((item) => item.id === queryConversationId)
          ? queryConversationId
          : items[0]?.id || '';

      syncSelectedConversation(nextConversationId);

      if (nextConversationId) {
        await fetchRuns(nextConversationId);
      } else {
        setRuns([]);
      }
    } catch (requestError) {
      setError(getErrorText(requestError));
    } finally {
      setConversationLoading(false);
    }
  };

  useEffect(() => {
    void fetchConversations();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleConversationChange = (conversationId: string): void => {
    syncSelectedConversation(conversationId);
    void fetchRuns(conversationId);
  };

  const openRunDetail = (runId: string): void => {
    const search = selectedConversationId
      ? `?conversation_id=${encodeURIComponent(selectedConversationId)}`
      : '';

    history.push(`/traces/${runId}${search}`);
  };

  const columns: ColumnsType<AgentRunItem> = [
    {
      title: '时间',
      dataIndex: 'created_at',
      width: 180,
      render: (value: string) => formatDateTime(value),
    },
    {
      title: '问题',
      dataIndex: 'input',
      ellipsis: true,
      render: (value: string) => (
        <Text ellipsis={{ tooltip: value }} className={styles.questionText}>
          {value || '-'}
        </Text>
      ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      width: 120,
      render: (value: string) => <Tag color={statusColor(value)}>{value}</Tag>,
    },
    {
      title: '步数',
      dataIndex: 'step_count',
      align: 'right',
      width: 90,
    },
    {
      title: '耗时',
      dataIndex: 'total_latency_ms',
      align: 'right',
      width: 110,
      render: (value: number | null) => formatLatency(value),
    },
    {
      title: '模型',
      dataIndex: 'model',
      width: 180,
      render: (value: string | null) => value || '-',
    },
    {
      title: '操作',
      key: 'action',
      width: 120,
      render: (_, record) => (
        <Button
          type="link"
          icon={<EyeOutlined />}
          onClick={() => openRunDetail(record.id)}
        >
          查看详情
        </Button>
      ),
    },
  ];

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <div>
          <Title level={2} className={styles.title}>
            Agent Trace
          </Title>
          <Paragraph className={styles.subtitle}>
            按会话查看 Agent Run、工具步骤和事件链路，用于排查执行过程。
          </Paragraph>
        </div>
        <Space wrap>
          <Button onClick={() => history.push('/')}>返回聊天</Button>
          <Button onClick={() => history.push('/docs')}>文档管理</Button>
        </Space>
      </div>

      <Card className={styles.card}>
        <Space className={styles.toolbar} wrap>
          <Select
            className={styles.conversationSelect}
            loading={conversationLoading}
            options={conversationOptions}
            placeholder="选择会话"
            value={selectedConversationId || undefined}
            onChange={handleConversationChange}
            showSearch
            optionFilterProp="label"
          />
          <Button
            icon={<ReloadOutlined />}
            loading={runsLoading || conversationLoading}
            onClick={() => {
              if (selectedConversationId) {
                void fetchRuns(selectedConversationId);
              } else {
                void fetchConversations();
              }
            }}
          >
            刷新
          </Button>
        </Space>
      </Card>

      {error ? (
        <Alert className={styles.alert} type="error" showIcon message={error} />
      ) : null}

      <Card className={styles.card} title="Run 列表">
        <Table<AgentRunItem>
          columns={columns}
          dataSource={runs}
          loading={runsLoading}
          rowKey="id"
          pagination={{ pageSize: 10, showSizeChanger: true }}
          scroll={{ x: 960 }}
          locale={{
            emptyText: selectedConversationId ? (
              <Empty description="当前会话暂无 Agent Run" />
            ) : (
              <Empty description="请先选择会话" />
            ),
          }}
          onRow={(record) => ({
            onDoubleClick: () => openRunDetail(record.id),
          })}
        />
      </Card>
    </div>
  );
};

export default AgentTracePage;
