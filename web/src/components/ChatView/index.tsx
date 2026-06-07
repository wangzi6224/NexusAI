import {
  FileTextOutlined,
  RadarChartOutlined,
} from '@ant-design/icons';
import { Badge, Popover, Typography } from 'antd';
import React, { useMemo } from 'react';
import { useChatContext } from '../../contexts/ChatContext';
import ChatInputBar from '../ChatInputBar';
import ChatMessageList from '../ChatMessageList';
import styles from './index.module.less';

const { Text } = Typography;

const ChatView: React.FC = () => {
  const {
    messages,
    currentProvider,
    currentModel,
    activeConversation,
    messagesLoading,
    } = useChatContext();

     // Count messages with agent trace info
  const traceableCount = useMemo(() => {
    if (!messages || messages.length === 0) return 0;
    return messages.filter((m) => m.assistantRunId).length;
     }, [messages]);

  const handleOpenDocs = (): void => {
    window.location.href = '/docs';
      };

  const handleOpenTraces = (): void => {
    window.location.href = '/traces';
      };

  return (
        <div className={styles.chatView}>
          {/* Header */}
          <div className={styles.chatHeader}>
            <div className={styles.chatHeaderTitle}>
              <Text className={styles.chatTitle} ellipsis>
                  {activeConversation?.title || '新会话'}
                  {currentModel
                    ? ` · ${
                      currentProvider ? `${currentProvider}/` : ''
                        }${currentModel}`
                    : ''}
                  </Text>
                </div>

              {/* Right-side quick tools */}
              <div className={styles.headerActions}>
                <Popover
                content="查看知识库文档管理"
                placement="bottom"
                  >
                    <FileTextOutlined
                    className={styles.headerActionBtn}
                    onClick={handleOpenDocs}
                      />
                    </Popover>

                    <Popover
                content={traceableCount > 0 ? `Agent 执行记录 (${traceableCount})` : '查看 Agent 执行链路'}
                placement="bottom"
                  >
                    <Badge
                    count={traceableCount > 0 ? traceableCount : undefined}
                      >
                        <RadarChartOutlined
                        className={styles.headerActionBtn}
                        onClick={handleOpenTraces}
                          />
                        </Badge>
                      </Popover>
                    </div>
                  </div>

                  {/* Messages */}
                  <div className={styles.messagesArea}>
                    <ChatMessageList messages={messages} loading={messagesLoading} />
                  </div>

                  {/* Input */}
                  <ChatInputBar />
                </div>
              );
           };

export default ChatView;
