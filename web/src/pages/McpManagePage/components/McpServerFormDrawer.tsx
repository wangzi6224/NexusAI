import {
  createMcpServer,
  updateMcpServer,
} from '@/services/mcpApi';
import { PlusOutlined } from '@ant-design/icons';
import {
  Alert,
  Button,
  Drawer,
  Form,
  Input,
  InputNumber,
  Select,
  Space,
  Switch,
  message,
} from 'antd';
import React, { useEffect, useMemo, useState } from 'react';
import styles from '../index.module.less';
import {
  McpServerConfig,
  McpServerCreatePayload,
  McpTransportType,
} from '../types';
import EnvKeyValueEditor, { EnvKeyValueItem } from './EnvKeyValueEditor';
import JsonEditorField from './JsonEditorField';

interface ServerFormValues {
  name: string;
  transport: McpTransportType;
  command: string;
  args: { value?: string }[];
  env: EnvKeyValueItem[];
  enabled: boolean;
  timeout_seconds: number;
  metadata: string;
}

interface McpServerFormDrawerProps {
  open: boolean;
  server?: McpServerConfig | null;
  onClose: () => void;
  onSuccess: () => void;
}

const stringifyJson = (value?: Record<string, unknown>): string =>
  JSON.stringify(value || {}, null, 2);

const envToItems = (env?: Record<string, string>): EnvKeyValueItem[] =>
  Object.entries(env || {}).map(([key, value]) => ({ key, value: value ? '******' : '' }));

const itemsToEnv = (items: EnvKeyValueItem[], original?: Record<string, string>) =>
  items.reduce<Record<string, string>>((acc, item) => {
    const key = item.key?.trim();
    if (!key) return acc;

    // 编辑时密码占位符代表沿用原值，避免明文回显后再提交。
    acc[key] = item.value === '******' ? original?.[key] || '' : item.value || '';
    return acc;
  }, {});

const McpServerFormDrawer: React.FC<McpServerFormDrawerProps> = ({
  open,
  server,
  onClose,
  onSuccess,
}) => {
  const [form] = Form.useForm<ServerFormValues>();
  const [submitting, setSubmitting] = useState(false);
  const [metadataError, setMetadataError] = useState('');
  const editing = Boolean(server);

  const initialValues = useMemo<ServerFormValues>(
    () => ({
      name: server?.name || '',
      transport: server?.transport || 'stdio',
      command: server?.command || '',
      args: (server?.args || []).map((value) => ({ value })),
      env: envToItems(server?.env),
      enabled: server?.enabled ?? true,
      timeout_seconds: server?.timeout_seconds || 15,
      metadata: stringifyJson(server?.metadata),
    }),
    [server],
  );

  useEffect(() => {
    if (!open) return;
    setMetadataError('');
    form.setFieldsValue(initialValues);
  }, [form, initialValues, open]);

  const parseMetadata = (text: string): Record<string, unknown> => {
    try {
      const parsed = JSON.parse(text || '{}') as unknown;
      if (!parsed || Array.isArray(parsed) || typeof parsed !== 'object') {
        throw new Error('metadata 必须是 JSON object');
      }
      setMetadataError('');
      return parsed as Record<string, unknown>;
    } catch (error) {
      const textError = error instanceof Error ? error.message : 'JSON 格式错误';
      setMetadataError(textError);
      throw error;
    }
  };

  const handleSubmit = async (): Promise<void> => {
    try {
      const values = await form.validateFields();
      const metadata = parseMetadata(values.metadata);
      const payload: McpServerCreatePayload = {
        name: values.name.trim(),
        transport: values.transport,
        command: values.command.trim(),
        args: (values.args || [])
          .map((item) => item.value?.trim())
          .filter((item): item is string => Boolean(item)),
        env: itemsToEnv(values.env || [], server?.env),
        enabled: values.enabled,
        timeout_seconds: values.timeout_seconds,
        metadata,
      };

      setSubmitting(true);

      if (editing && server) {
        await updateMcpServer(server.name, {
          command: payload.command,
          args: payload.args,
          env: payload.env,
          enabled: payload.enabled,
          timeout_seconds: payload.timeout_seconds,
          metadata: payload.metadata,
        });
        message.success('MCP Server 已更新');
      } else {
        await createMcpServer(payload);
        message.success('MCP Server 已注册');
      }

      onSuccess();
      onClose();
    } catch (error) {
      if (error instanceof Error && error.message) {
        message.error(error.message);
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <Drawer
      title={editing ? '编辑 MCP Server' : '注册 MCP Server'}
      width={560}
      open={open}
      onClose={onClose}
      destroyOnClose
      extra={
        <Space>
          <Button onClick={onClose}>取消</Button>
          <Button type="primary" loading={submitting} onClick={handleSubmit}>
            提交
          </Button>
        </Space>
      }
    >
      <Alert
        className={styles.alert}
        type="info"
        showIcon
        message="发现工具不等于授权。外部 MCP Server 发现出的工具仍需单独启用。"
      />
      <Form form={form} layout="vertical" initialValues={initialValues}>
        <Form.Item
          label="name"
          name="name"
          rules={[
            { required: true, message: '请输入 MCP Server 名称' },
            {
              pattern: /^[A-Za-z0-9_-]+$/,
              message: '仅允许字母、数字、下划线和中划线',
            },
            {
              validator: (_, value: string) =>
                value?.includes('__')
                  ? Promise.reject(new Error('name 不能包含 "__"'))
                  : Promise.resolve(),
            },
          ]}
        >
          <Input disabled={editing} placeholder="例如 filesystem" />
        </Form.Item>
        <Form.Item label="transport" name="transport" rules={[{ required: true }]}>
          <Select
            options={[
              { label: 'stdio', value: 'stdio' },
              {
                label: 'SSE/HTTP（后端暂未支持）',
                value: 'SSE/HTTP',
                disabled: true,
              },
              {
                label: 'Streaming HTTP（后端暂未支持）',
                value: 'Streaming HTTP',
                disabled: true,
              },
            ]}
          />
        </Form.Item>
        <Form.Item
          label="command"
          name="command"
          rules={[{ required: true, message: '请输入启动命令' }]}
        >
          <Input placeholder="例如 npx / uvx / python / node" />
        </Form.Item>
        <Form.List name="args">
          {(fields, { add, remove }) => (
            <div className={styles.argList}>
              {fields.map((field) => (
                <Space key={field.key} align="baseline" className={styles.argRow}>
                  <Form.Item {...field} name={[field.name, 'value']}>
                    <Input placeholder="参数" />
                  </Form.Item>
                  <Button onClick={() => remove(field.name)}>删除</Button>
                </Space>
              ))}
              <Button
                type="dashed"
                icon={<PlusOutlined />}
                onClick={() => add({ value: '' })}
                block
              >
                添加参数
              </Button>
            </div>
          )}
        </Form.List>
        <Form.Item label="env">
          <EnvKeyValueEditor name="env" />
        </Form.Item>
        <Form.Item label="enabled" name="enabled" valuePropName="checked">
          <Switch checkedChildren="启用" unCheckedChildren="停用" />
        </Form.Item>
        <Form.Item
          label="timeout_seconds"
          name="timeout_seconds"
          rules={[{ required: true, message: '请输入超时时间' }]}
        >
          <InputNumber min={1} max={120} className={styles.fullWidth} />
        </Form.Item>
        <Form.Item label="metadata" name="metadata">
          <JsonEditorField error={metadataError} />
        </Form.Item>
      </Form>
    </Drawer>
  );
};

export default McpServerFormDrawer;
