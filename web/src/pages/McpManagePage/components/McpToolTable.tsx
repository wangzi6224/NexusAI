import { EyeOutlined, PlayCircleOutlined } from '@ant-design/icons';
import {
  Button,
  Popconfirm,
  Select,
  Space,
  Switch,
  Table,
  Tag,
  Typography,
} from 'antd';
import type { ColumnsType } from 'antd/es/table';
import React from 'react';
import styles from '../index.module.less';
import { McpRiskLevel, McpToolSpec } from '../types';

const { Paragraph, Text } = Typography;

interface McpToolTableProps {
  tools: McpToolSpec[];
  loading: boolean;
  updatingToolName: string;
  onToggle: (tool: McpToolSpec, enabled: boolean) => void;
  onRiskChange: (tool: McpToolSpec, riskLevel: McpRiskLevel) => void;
  onOpenDetail: (tool: McpToolSpec, tab?: string) => void;
}

const riskColorMap: Record<McpRiskLevel, string> = {
  low: 'green',
  medium: 'gold',
  high: 'red',
};

const McpToolTable: React.FC<McpToolTableProps> = ({
  tools,
  loading,
  updatingToolName,
  onToggle,
  onRiskChange,
  onOpenDetail,
}) => {
  const columns: ColumnsType<McpToolSpec> = [
    {
      title: 'tool_name',
      dataIndex: 'tool_name',
      width: 170,
      render: (value: string) => <Text strong>{value}</Text>,
    },
    {
      title: 'full_name',
      dataIndex: 'full_name',
      width: 260,
      render: (value: string) => <Text code>{value}</Text>,
    },
    {
      title: 'description',
      dataIndex: 'description',
      render: (value: string) => (
        <Paragraph className={styles.tableParagraph} ellipsis={{ rows: 2, tooltip: value }}>
          {value || '-'}
        </Paragraph>
      ),
    },
    {
      title: 'risk_level',
      dataIndex: 'risk_level',
      width: 170,
      render: (value: McpRiskLevel, record) => (
        <Select
          size="small"
          value={value}
          className={styles.riskSelect}
          onChange={(nextValue) => onRiskChange(record, nextValue)}
          options={[
            { label: <Tag color={riskColorMap.low}>low</Tag>, value: 'low' },
            { label: <Tag color={riskColorMap.medium}>medium</Tag>, value: 'medium' },
            { label: <Tag color={riskColorMap.high}>high</Tag>, value: 'high' },
          ]}
        />
      ),
    },
    {
      title: 'enabled',
      dataIndex: 'enabled',
      width: 120,
      render: (enabled: boolean, record) => {
        const control = (
          <Switch
            size="small"
            checked={enabled}
            loading={updatingToolName === record.full_name}
            onChange={(nextEnabled) => {
              if (nextEnabled && record.risk_level === 'high') return;
              onToggle(record, nextEnabled);
            }}
          />
        );

        if (!enabled && record.risk_level === 'high') {
          return (
            <Popconfirm
              title="启用高风险工具"
              description="该工具被标记为高风险。启用后 Agent 可能在授权范围内调用它。确认启用？"
              okText="确认启用"
              cancelText="取消"
              onConfirm={() => onToggle(record, true)}
            >
              {control}
            </Popconfirm>
          );
        }

        return control;
      },
    },
    {
      title: 'input_schema',
      width: 120,
      render: (_, record) => (
        <Button size="small" onClick={() => onOpenDetail(record, 'schema')}>
          查看
        </Button>
      ),
    },
    {
      title: '操作',
      width: 180,
      render: (_, record) => (
        <Space wrap>
          <Button size="small" icon={<EyeOutlined />} onClick={() => onOpenDetail(record, 'base')}>
            详情
          </Button>
          <Button
            size="small"
            icon={<PlayCircleOutlined />}
            onClick={() => onOpenDetail(record, 'test')}
          >
            测试调用
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <Table
      rowKey="full_name"
      size="middle"
      loading={loading}
      columns={columns}
      dataSource={tools}
      pagination={false}
      scroll={{ x: 1180 }}
      locale={{ emptyText: '暂无工具。发现工具后仍需单独授权启用。' }}
    />
  );
};

export { riskColorMap };
export default McpToolTable;
