import { DeleteOutlined, PlusOutlined } from '@ant-design/icons';
import { Button, Form, Input, Space } from 'antd';
import React from 'react';
import styles from '../index.module.less';

export interface EnvKeyValueItem {
  key?: string;
  value?: string;
}

interface EnvKeyValueEditorProps {
  name: string;
}

const EnvKeyValueEditor: React.FC<EnvKeyValueEditorProps> = ({ name }) => {
  return (
    <Form.List name={name}>
      {(fields, { add, remove }) => (
        <div className={styles.envEditor}>
          {fields.map((field) => (
            <Space key={field.key} align="baseline" className={styles.envRow}>
              <Form.Item
                {...field}
                name={[field.name, 'key']}
                rules={[
                  {
                    pattern: /^[A-Za-z_][A-Za-z0-9_]*$/,
                    message: '仅支持环境变量格式的 key',
                  },
                ]}
              >
                <Input placeholder="KEY" />
              </Form.Item>
              <Form.Item {...field} name={[field.name, 'value']}>
                <Input.Password placeholder="VALUE" autoComplete="new-password" />
              </Form.Item>
              <Button
                aria-label="删除环境变量"
                icon={<DeleteOutlined />}
                onClick={() => remove(field.name)}
              />
            </Space>
          ))}
          <Button
            type="dashed"
            icon={<PlusOutlined />}
            onClick={() => add({ key: '', value: '' })}
            block
          >
            添加环境变量
          </Button>
        </div>
      )}
    </Form.List>
  );
};

export default EnvKeyValueEditor;
