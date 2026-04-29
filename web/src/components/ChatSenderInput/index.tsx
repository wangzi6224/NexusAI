import { Sender } from '@ant-design/x';
import { Button, Flex } from 'antd';
import classNames from 'classnames';
import React, { useState } from 'react';
import { useChatContext } from '../../contexts/ChatContext';
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

  const handleSubmit = (val: string) => {
    if (!val.trim() || loading) return;
    sendMessage(val.trim());
    setInputValue('');
  };

  const handleKeyDown = (e: React.KeyboardEvent): false | void => {
    if (
      e.key === 'Enter' &&
      !e.shiftKey &&
      !e.ctrlKey &&
      !e.altKey &&
      !e.metaKey
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
          <Flex align="center" justify="flex-end" gap={8} className="w-full">
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
