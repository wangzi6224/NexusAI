import {
  deleteMcpServer,
  discoverMcpTools,
  listMcpAuditLogs,
  listMcpServers,
  listMcpTools,
  updateMcpServer,
  updateMcpTool,
} from '@/services/mcpApi';
import {
  ApiOutlined,
  PlusOutlined,
  ReloadOutlined,
  SafetyCertificateOutlined,
  ToolOutlined,
} from '@ant-design/icons';
import {
  Alert,
  Button,
  Card,
  Col,
  Empty,
  Row,
  Space,
  Table,
  Tag,
  Typography,
  message,
} from 'antd';
import type { ColumnsType } from 'antd/es/table';
import axios from 'axios';
import React, { useEffect, useMemo, useState } from 'react';
import McpServerFormDrawer from './components/McpServerFormDrawer';
import McpServerTable from './components/McpServerTable';
import McpToolDetailDrawer from './components/McpToolDetailDrawer';
import McpToolTable from './components/McpToolTable';
import styles from './index.module.less';
import { McpAuditLog, McpRiskLevel, McpServerConfig, McpToolSpec } from './types';

const { Text, Title } = Typography;

const getErrorText = (error: unknown): string => {
  if (axios.isAxiosError(error)) {
    const data = error.response?.data as
      | { message?: string; detail?: unknown; code?: string }
      | undefined;
    const detailText =
      typeof data?.detail === 'string' ? data.detail : undefined;
    return data?.message || detailText || data?.code || error.message || '请求失败';
  }

  return error instanceof Error ? error.message : '请求失败';
};

const withToolCounts = (
  servers: McpServerConfig[],
  tools: McpToolSpec[],
): McpServerConfig[] => {
  const countMap = tools.reduce<Record<string, number>>((acc, tool) => {
    acc[tool.server_name] = (acc[tool.server_name] || 0) + 1;
    return acc;
  }, {});

  return servers.map((server) => ({
    ...server,
    tool_count: server.tool_count ?? countMap[server.name] ?? 0,
  }));
};

const McpManagePage: React.FC = () => {
  const [servers, setServers] = useState<McpServerConfig[]>([]);
  const [tools, setTools] = useState<McpToolSpec[]>([]);
  const [auditLogs, setAuditLogs] = useState<McpAuditLog[]>([]);
  const [selectedServerName, setSelectedServerName] = useState('');
  const [serversLoading, setServersLoading] = useState(false);
  const [toolsLoading, setToolsLoading] = useState(false);
  const [auditLoading, setAuditLoading] = useState(false);
  const [pageError, setPageError] = useState('');
  const [auditError, setAuditError] = useState('');
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [editingServer, setEditingServer] = useState<McpServerConfig | null>(null);
  const [discoveringServerName, setDiscoveringServerName] = useState('');
  const [updatingToolName, setUpdatingToolName] = useState('');
  const [detailTool, setDetailTool] = useState<McpToolSpec | null>(null);
  const [detailTab, setDetailTab] = useState('base');

  const selectedServer = useMemo(
    () => servers.find((item) => item.name === selectedServerName) || null,
    [selectedServerName, servers],
  );

  const selectedTools = useMemo(
    () => tools.filter((tool) => tool.server_name === selectedServerName),
    [selectedServerName, tools],
  );

  const stats = useMemo(
    () => ({
      servers: servers.length,
      enabledServers: servers.filter((item) => item.enabled).length,
      tools: tools.length,
      highRiskTools: tools.filter((item) => item.risk_level === 'high').length,
    }),
    [servers, tools],
  );

  const fetchAuditLogs = async (): Promise<void> => {
    setAuditLoading(true);
    setAuditError('');

    try {
      const response = await listMcpAuditLogs({ limit: 20 });
      setAuditLogs(response.items || []);
    } catch (error) {
      setAuditLogs([]);
      setAuditError(getErrorText(error) || '审计日志接口暂不可用，等待后端补齐');
    } finally {
      setAuditLoading(false);
    }
  };

  const fetchAll = async (): Promise<void> => {
    setServersLoading(true);
    setToolsLoading(true);
    setPageError('');

    try {
      const [serverResponse, toolResponse] = await Promise.all([
        listMcpServers(),
        listMcpTools(),
      ]);
      const serverItems = serverResponse.items || [];
      const toolItems = toolResponse.items || [];
      setServers(withToolCounts(serverItems, toolItems));
      setTools(toolItems);
      setSelectedServerName((current) => {
        if (current && serverItems.some((server) => server.name === current)) {
          return current;
        }
        return serverItems[0]?.name || '';
      });
    } catch (error) {
      setPageError(getErrorText(error));
      setServers([]);
      setTools([]);
    } finally {
      setServersLoading(false);
      setToolsLoading(false);
    }

    void fetchAuditLogs();
  };

  useEffect(() => {
    void fetchAll();
  }, []);

  const handleDiscover = async (server: McpServerConfig): Promise<void> => {
    setDiscoveringServerName(server.name);

    try {
      const response = await discoverMcpTools(server.name);
      message.success(`发现 ${response.discovered_count} 个工具，已保存 ${response.saved_count} 个`);
      await fetchAll();
      setSelectedServerName(server.name);
    } catch (error) {
      message.error(`发现工具失败：${getErrorText(error)}`);
    } finally {
      setDiscoveringServerName('');
    }
  };

  const handleServerToggle = async (
    server: McpServerConfig,
    enabled: boolean,
  ): Promise<void> => {
    try {
      await updateMcpServer(server.name, { enabled });
      message.success(enabled ? 'Server 已启用' : 'Server 已停用');
      await fetchAll();
    } catch (error) {
      message.error(getErrorText(error));
    }
  };

  const handleDeleteServer = async (server: McpServerConfig): Promise<void> => {
    try {
      await deleteMcpServer(server.name);
      message.success('MCP Server 已删除');
      await fetchAll();
    } catch (error) {
      message.error(getErrorText(error));
    }
  };

  const handleToolToggle = async (
    tool: McpToolSpec,
    enabled: boolean,
  ): Promise<void> => {
    setUpdatingToolName(tool.full_name);

    try {
      const updated = await updateMcpTool(tool.server_name, tool.tool_name, {
        enabled,
      });
      setTools((current) =>
        current.map((item) => (item.full_name === updated.full_name ? updated : item)),
      );
      message.success(enabled ? '工具已启用' : '工具已停用');
    } catch (error) {
      message.error(getErrorText(error));
    } finally {
      setUpdatingToolName('');
    }
  };

  const handleRiskChange = async (
    tool: McpToolSpec,
    riskLevel: McpRiskLevel,
  ): Promise<void> => {
    setUpdatingToolName(tool.full_name);

    try {
      const updated = await updateMcpTool(tool.server_name, tool.tool_name, {
        risk_level: riskLevel,
      });
      setTools((current) =>
        current.map((item) => (item.full_name === updated.full_name ? updated : item)),
      );
      message.success('风险等级已更新');
    } catch (error) {
      message.error(getErrorText(error));
    } finally {
      setUpdatingToolName('');
    }
  };

  const openServerDrawer = (server?: McpServerConfig): void => {
    setEditingServer(server || null);
    setDrawerOpen(true);
  };

  const openToolDetail = (tool: McpToolSpec, tab = 'base'): void => {
    setDetailTool(tool);
    setDetailTab(tab);
  };

  const auditColumns: ColumnsType<McpAuditLog> = [
    {
      title: 'tool',
      dataIndex: 'full_tool_name',
      render: (value: string) => <Text code>{value}</Text>,
    },
    {
      title: 'risk',
      dataIndex: 'risk_level',
      width: 100,
      render: (value: McpRiskLevel) => (
        <Tag color={value === 'high' ? 'red' : value === 'medium' ? 'gold' : 'green'}>
          {value}
        </Tag>
      ),
    },
    {
      title: 'success',
      dataIndex: 'success',
      width: 100,
      render: (value: boolean) => (
        <Tag color={value ? 'green' : 'red'}>{String(value)}</Tag>
      ),
    },
    {
      title: 'latency',
      dataIndex: 'latency_ms',
      width: 100,
      render: (value: number) => `${value || 0}ms`,
    },
    {
      title: 'error',
      dataIndex: 'error_message',
      render: (value?: string | null) => value || '-',
    },
  ];

  return (
    <div className={styles.page}>
      <div className={styles.header}>
        <div>
          <Title level={2} className={styles.title}>
            MCP 管理
          </Title>
          <Text className={styles.subtitle}>
            注册、发现、授权和审计外部 MCP Server 工具
          </Text>
        </div>
        <Space wrap>
          <Button icon={<ReloadOutlined />} onClick={() => void fetchAll()}>
            刷新
          </Button>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => openServerDrawer()}
          >
            注册 MCP Server
          </Button>
        </Space>
      </div>

      <Row gutter={[16, 16]} className={styles.summaryGrid}>
        <Col xs={24} sm={12} lg={6}>
          <div className={styles.metric}>
            <ApiOutlined className={styles.metricIcon} />
            <Text className={styles.metricLabel}>MCP Server 数</Text>
            <strong>{stats.servers}</strong>
          </div>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <div className={styles.metric}>
            <SafetyCertificateOutlined className={styles.metricIcon} />
            <Text className={styles.metricLabel}>启用 Server 数</Text>
            <strong>{stats.enabledServers}</strong>
          </div>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <div className={styles.metric}>
            <ToolOutlined className={styles.metricIcon} />
            <Text className={styles.metricLabel}>已发现工具数</Text>
            <strong>{stats.tools}</strong>
          </div>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <div className={styles.metric}>
            <SafetyCertificateOutlined className={styles.metricIconDanger} />
            <Text className={styles.metricLabel}>高风险工具数</Text>
            <strong>{stats.highRiskTools}</strong>
          </div>
        </Col>
      </Row>

      {pageError ? (
        <Alert className={styles.alert} type="error" showIcon message={pageError} />
      ) : null}

      <Card className={styles.card} title="MCP Server">
        <McpServerTable
          servers={servers}
          selectedServerName={selectedServerName}
          loading={serversLoading}
          discoveringServerName={discoveringServerName}
          onSelect={(server) => setSelectedServerName(server.name)}
          onEdit={openServerDrawer}
          onDiscover={(server) => void handleDiscover(server)}
          onToggle={(server, enabled) => void handleServerToggle(server, enabled)}
          onDelete={(server) => void handleDeleteServer(server)}
        />
      </Card>

      <Card
        className={styles.card}
        title={selectedServer ? `工具列表：${selectedServer.name}` : '工具列表'}
        extra={<Text type="secondary">发现不等于授权，工具启用状态需单独确认</Text>}
      >
        {selectedServer ? (
          <McpToolTable
            tools={selectedTools}
            loading={toolsLoading}
            updatingToolName={updatingToolName}
            onToggle={(tool, enabled) => void handleToolToggle(tool, enabled)}
            onRiskChange={(tool, riskLevel) => void handleRiskChange(tool, riskLevel)}
            onOpenDetail={openToolDetail}
          />
        ) : (
          <Empty description="请选择 MCP Server" />
        )}
      </Card>

      <Card className={styles.card} title="最近审计日志">
        {auditError ? (
          <Alert
            className={styles.alert}
            type="info"
            showIcon
            message="审计日志接口暂不可用"
            description={auditError}
          />
        ) : null}
        <Table
          rowKey="id"
          loading={auditLoading}
          columns={auditColumns}
          dataSource={auditLogs}
          pagination={false}
          locale={{ emptyText: '暂无审计记录' }}
        />
      </Card>

      <McpServerFormDrawer
        open={drawerOpen}
        server={editingServer}
        onClose={() => setDrawerOpen(false)}
        onSuccess={() => void fetchAll()}
      />
      <McpToolDetailDrawer
        open={Boolean(detailTool)}
        tool={detailTool}
        activeTab={detailTab}
        onClose={() => setDetailTool(null)}
      />
    </div>
  );
};

export default McpManagePage;
