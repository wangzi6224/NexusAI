import { GlobalOutlined } from '@ant-design/icons';
import { Sender } from '@ant-design/x';
import { Button, Flex, Select } from 'antd';
import classNames from 'classnames';
import React, { useState } from 'react';
import { CATEGORY_OPTIONS, useChatContext } from '../../contexts/ChatContext';
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
  const {
    networkEnabled,
    setNetworkEnabled,
    selectedCategory,
    setSelectedCategory,
    sendMessage,
  } = useChatContext();

  const [inputValue, setInputValue] = useState('');

  const handleSubmit = (val: string) => {
    if (!val.trim()) return;
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
        placeholder="询问任何问题前，先选择板块，回答会更精准～"
        autoSize={autoSize}
        footer={
          <Flex
            align="center"
            justify="space-between"
            gap={8}
            className={classNames(['w-full'])}
          >
            <Flex align="center" justify="space-between" gap={16}>
              <Button
                className={classNames(styles.networkBtn, {
                  [styles.networkBtnActive]: networkEnabled,
                })}
                icon={<GlobalOutlined />}
                size="small"
                onClick={() => {
                  setNetworkEnabled(!networkEnabled);
                  localStorage.setItem(
                    'networkEnabled',
                    (!networkEnabled).toString(),
                  );
                }}
              >
                联网开关
              </Button>
              <Select
                className={styles.categorySelect}
                value={selectedCategory}
                onChange={(e) => {
                  setSelectedCategory(e);
                  localStorage.setItem('selectedCategory', e);
                }}
                options={CATEGORY_OPTIONS}
              />
            </Flex>
            <Button
              type="primary"
              className={styles.sendBtn}
              onClick={() => handleSubmit(inputValue)}
              disabled={!inputValue.trim()}
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
