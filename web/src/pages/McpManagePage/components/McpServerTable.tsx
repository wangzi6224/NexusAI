import {
  DeleteOutlined,
  EditOutlined,
  EyeOutlined,
  SearchOutlined,
} from '@ant-design/icons';
import { Badge, Button, Popconfirm, Space, Switch, Table, Tag, Typography } from 'antd';
import type { ColumnsType } from 'antd/es/table';
import React from 'react';
import styles from '../index.module.less';
import { McpServerConfig } from '../types';

const { Text } = Typography;

interface McpServerTableProps {
  servers: McpServerConfig[];
  selectedServerName: string;
  loading: boolean;
  discoveringServerName: string;
  onSelect: (server: McpServerConfig) => void;
  onEdit: (server: McpServerConfig) => void;
  onDiscover: (server: McpServerConfig) => void;
  onToggle: (server: McpServerConfig, enabled: boolean) => void;
  onDelete: (server: McpServerConfig) => void;
}

const formatDateTime = (value?: string | null): string => {
  if (!value) return '-';
  const date = new Date(value);
  return Number.isNaN(date.getTime())
    ? value
    : date.toLocaleString('zh-CN', { hour12: false });
};

const getLastDiscoveredAt = (server: McpServerConfig): string | null => {
  const metadataValue = server.metadata?.last_discovered_at;
  return (
    server.last_discovered_at ||
    (typeof metadataValue === 'string' ? metadataValue : null)
  );
};

const McpServerTable: React.FC<McpServerTableProps> = ({
  servers,
  selectedServerName,
  loading,
  discoveringServerName,
  onSelect,
  onEdit,
  onDiscover,
  onToggle,
  onDelete,
}) => {
  const columns: ColumnsType<McpServerConfig> = [
    {
      title: 'name',
      dataIndex: 'name',
      fixed: 'left',
      width: 160,
      render: (value: string, record) => (
        <Button type="link" onClick={() => onSelect(record)} className={styles.linkButton}>
          {value}
        </Button>
      ),
    },
    {
      title: 'transport',
      dataIndex: 'transport',
      width: 120,
      render: (value: string) => <Tag color="blue">{value}</Tag>,
    },
    {
      title: 'command',
      dataIndex: 'command',
      width: 160,
      render: (value: string) => <Text code>{value}</Text>,
    },
    {
      title: 'args',
      dataIndex: 'args',
      width: 220,
      render: (value: string[]) => (
        <Text ellipsis={{ tooltip: value?.join(' ') || '-' }}>
          {value?.join(' ') || '-'}
        </Text>
      ),
    },
    {
      title: 'enabled',
      dataIndex: 'enabled',
      width: 110,
      render: (enabled: boolean, record) => (
        <Switch
          size="small"
          checked={enabled}
          onChange={(nextEnabled) => onToggle(record, nextEnabled)}
        />
      ),
    },
    {
      title: 'timeout',
      dataIndex: 'timeout_seconds',
      width: 100,
      render: (value: number) => `${value}s`,
    },
    {
      title: 'tools',
      dataIndex: 'tool_count',
      width: 90,
      render: (value?: number) => value ?? 0,
    },
    {
      title: 'last_discovered_at',
      width: 180,
      render: (_, record) => formatDateTime(getLastDiscoveredAt(record)),
    },
    {
      title: '状态',
      width: 90,
      render: (_, record) => (
        <Badge status={record.enabled ? 'success' : 'default'} text={record.enabled ? '启用' : '停用'} />
      ),
    },
    {
      title: '操作',
      fixed: 'right',
      width: 300,
      render: (_, record) => (
        <Space wrap>
          <Button size="small" icon={<EyeOutlined />} onClick={() => onSelect(record)}>
            查看工具
          </Button>
          <Button size="small" icon={<EditOutlined />} onClick={() => onEdit(record)}>
            编辑
          </Button>
          <Button
            size="small"
            icon={<SearchOutlined />}
            loading={discoveringServerName === record.name}
            onClick={() => onDiscover(record)}
          >
            发现工具
          </Button>
          <Popconfirm
            title="删除 MCP Server"
            description="确定要删除该 Server 及其工具配置吗？"
            okText="删除"
            cancelText="取消"
            onConfirm={() => onDelete(record)}
          >
            <Button size="small" danger icon={<DeleteOutlined />}>
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <Table
      rowKey="name"
      size="middle"
      loading={loading}
      columns={columns}
      dataSource={servers}
      pagination={false}
      scroll={{ x: 1500 }}
      rowClassName={(record) =>
        record.name === selectedServerName ? styles.selectedRow : ''
      }
      locale={{
        emptyText: '暂无 MCP Server，请先注册外部 MCP Server',
      }}
    />
  );
};

export default McpServerTable;
