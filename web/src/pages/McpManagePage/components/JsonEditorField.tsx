import { Input, Typography } from 'antd';
import React from 'react';
import styles from '../index.module.less';

const { Text } = Typography;

interface JsonEditorFieldProps {
  value?: string;
  onChange?: (value: string) => void;
  rows?: number;
  placeholder?: string;
  error?: string;
}

const JsonEditorField: React.FC<JsonEditorFieldProps> = ({
  value,
  onChange,
  rows = 8,
  placeholder = '{\n  "key": "value"\n}',
  error,
}) => {
  return (
    <div>
      <Input.TextArea
        className={styles.jsonTextArea}
        value={value}
        onChange={(event) => onChange?.(event.target.value)}
        rows={rows}
        placeholder={placeholder}
      />
      {error ? (
        <Text type="danger" className={styles.fieldHint}>
          {error}
        </Text>
      ) : null}
    </div>
  );
};

export default JsonEditorField;
