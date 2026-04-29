import { useChatContext } from '@/contexts/ChatContext';
import {
  CheckCircleOutlined,
  ExclamationCircleOutlined,
} from '@ant-design/icons';
import { Badge, Typography } from 'antd';
import React from 'react';
import ChatSenderInput from '../ChatSenderInput';
import styles from './index.module.less';

const { Text, Title } = Typography;

const WelcomeScreen: React.FC = () => {
  const { health, healthError, currentModel } = useChatContext();

  return (
    <div className={styles.container}>
      <div className={styles.bgPattern} />

      <div className={styles.content}>
        <div className={styles.titleWrapper}>
          <Title level={2} className={styles.title}>
            My Python AI App
          </Title>
          <Text className={styles.subtitle}>
            基于 FastAPI 后端接口的模型对话前端
          </Text>

          <div className={styles.healthStatus}>
            {healthError ? (
              <Badge
                status="error"
                text={
                  <Text type="danger" className={styles.healthText}>
                    <ExclamationCircleOutlined className={styles.healthIcon} />
                    {healthError}
                  </Text>
                }
              />
            ) : health ? (
              <Badge
                status="success"
                text={
                  <Text className={styles.healthTextSuccess}>
                    <CheckCircleOutlined className={styles.healthIcon} />
                    后端在线
                    {currentModel ? `，当前模型：${currentModel}` : ''}
                  </Text>
                }
              />
            ) : (
              <Badge status="processing" text="正在连接后端…" />
            )}
          </div>
        </div>

        <div className={styles.inputWrapper}>
          <ChatSenderInput autoSize={{ minRows: 7, maxRows: 7 }} />
        </div>
      </div>
    </div>
  );
};

export default WelcomeScreen;
