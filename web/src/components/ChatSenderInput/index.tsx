import { Sender } from '@ant-design/x';
import { Button, Flex, Segmented, Tooltip } from 'antd';
import classNames from 'classnames';
import React, { useState } from 'react';
import { useChatContext } from '../../contexts/ChatContext';
import { AssistantMode } from '../../services/api';
import styles from './index.module.less';

export interface ChatSenderInputProps {
  /** textarea 最小最大行数 */
  autoSize?: { minRows?: number; maxRows?: number };
  /** 外层包裹 div 的额外 className */
  className?: string;
  /** Sender 组件的额外 className */
  senderClassName?: string;
}

const ChatSenderInput: React.FC<ChatSenderInputProps> = ({
  autoSize = { minRows: 2, maxRows: 6 },
  className,
  senderClassName,
}) => {
  const { sendMessage, loading } = useChatContext();

  const [inputValue, setInputValue] = useState('');
  const [mode, setMode] = useState<AssistantMode>('auto');

  const handleSubmit = (val: string) => {
    if (!val.trim() || loading) return;
    sendMessage(val.trim(), { mode });
    setInputValue('');
  };

  const handleKeyDown = (e: React.KeyboardEvent): false | void => {
    if (
      e.key === 'Enter' &&
      !e.shiftKey &&
      !e.ctrlKey &&
      !e.altKey &&
      !e.metaKey &&
      !e.nativeEvent.isComposing
    ) {
      e.preventDefault();
      handleSubmit(inputValue);
      return false;
    }
  };

  return (
    <div className={classNames(styles.wrapper, className)}>
      <Sender
        className={classNames(styles.sender, senderClassName)}
        value={inputValue}
        onChange={setInputValue}
        suffix={false}
        onSubmit={handleSubmit}
        onKeyDown={handleKeyDown}
        submitType="enter"
        placeholder="请输入你的问题"
        autoSize={autoSize}
        loading={loading}
        footer={
          <Flex
            align="center"
            justify="space-between"
            gap={8}
            className={styles.footer}
          >
            <Tooltip title="自动会按问题类型选择；MCP = 使用外部工具，不是新的回答模式">
              <Segmented
                size="small"
                value={mode}
                onChange={(value) => setMode(value as AssistantMode)}
                options={[
                  { label: '自动', value: 'auto' },
                  { label: '普通', value: 'chat' },
                  { label: 'Agent', value: 'agent' },
                  { label: 'MCP 外部工具', value: 'mcp' },
                ]}
                className={styles.modeSegmented}
              />
            </Tooltip>
            <Button
              type="primary"
              className={styles.sendBtn}
              onClick={() => handleSubmit(inputValue)}
              disabled={!inputValue.trim() || loading}
            >
              发送
            </Button>
          </Flex>
        }
      />
    </div>
  );
};

export default ChatSenderInput;
